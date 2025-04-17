module control (
    input logic reset,
    input logic clk,

    input logic [31:0] inst,
    input logic alu_zero,

    // enables
    output logic pc_en,
    output logic inst_en,
    output logic reg_wren,
    output logic mem_wren,

    // controls
    output imm_ctrl_t imm_ctrl,
    output alu_ctrl_t alu_ctrl,

    // mux selectors
    output mem_addr_sel_t mem_addr_sel,
    output mem_funct3_sel_t mem_funct3_sel,
    output alu_src1_sel_t alu_src1_sel,
    output alu_src2_sel_t alu_src2_sel,
    output result_sel_t result_sel
);
  alu_ops_t alu_op;
  logic pc_update;

  alu_decoder ad0 (
      .alu_op(alu_op),
      .funct3(inst[14:12]),
      .funct7_5(inst[30]),
      .op_5(inst[5]),
      .alu_ctrl(alu_ctrl)
  );

  imm_decoder id0 (
      .opcode  (inst[6:0]),
      .imm_ctrl(imm_ctrl)
  );

  fsm f0 (
      .reset(reset),
      .clk(clk),
      .opcode(inst[6:0]),

      .branch(branch),
      .pc_update(pc_update),
      .inst_en(inst_en),
      .reg_wren(reg_wren),
      .mem_wren(mem_wren),
      .mem_addr_sel(mem_addr_sel),
      .mem_funct3_sel(mem_funct3_sel),
      .alu_src1_sel(alu_src1_sel),
      .alu_src2_sel(alu_src2_sel),
      .result_sel(result_sel),
      .alu_op(alu_op)
  );

  assign pc_en = (branch && alu_zero) || pc_update;
endmodule

module alu_decoder (
    input alu_ops_t alu_op,
    input logic [2:0] funct3,

    // need these to distinguish between add/sub, and srl/sra
    input logic funct7_5,
    input logic op_5,

    output alu_ctrl_t alu_ctrl
);

  always_comb begin
    alu_ctrl = ADD;  // pick a default
    case (alu_op)
      ADD_OP: begin
        alu_ctrl = ADD;
      end
      SUB_OP: begin
        alu_ctrl = SUB;
      end
      FUNCT_DEFINED: begin
        case (funct3)
          3'b000: begin
            // op_5 confirms R-TYPE, funct7 signifies subtract
            // if op_5 is not true, this is I-TYPE
            if (op_5 & funct7_5) alu_ctrl = SUB;
            else alu_ctrl = ADD;
          end
          3'b001:  alu_ctrl = SLL;
          3'b010:  alu_ctrl = SLT;
          3'b011:  alu_ctrl = SLTU;
          3'b100:  alu_ctrl = XOR;
          3'b101: begin
            if (funct7_5) alu_ctrl = SRA;
            else alu_ctrl = SRL;
          end
          3'b110:  alu_ctrl = OR;
          3'b111:  alu_ctrl = AND;
          default: ;
        endcase
      end
      default: ;
    endcase
  end
endmodule

module imm_decoder (
    input logic [6:0] opcode,
    output imm_ctrl_t imm_ctrl
);

  always_comb begin
    imm_ctrl = ITYPE;
    case (opcode)
      `OP_ITYPE, `OP_LOAD, `OP_JALR: imm_ctrl = ITYPE;
      `OP_STYPE: imm_ctrl = STYPE;
      `OP_BTYPE: imm_ctrl = BTYPE;
      `OP_LUI, `OP_AUIPC: imm_ctrl = UTYPE;
      `OP_JAL: imm_ctrl = JTYPE;
      default: ;
    endcase
  end
endmodule
