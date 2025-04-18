module fsm (
    input logic reset,
    input logic clk,

    input logic [6:0] opcode,

    output logic branch,

    output logic pc_update,
    output logic inst_en,
    output logic reg_wren,
    output logic mem_wren,

    output mem_addr_sel_t mem_addr_sel,
    output mem_funct3_sel_t mem_funct3_sel,
    output alu_src1_sel_t alu_src1_sel,
    output alu_src2_sel_t alu_src2_sel,
    output result_sel_t result_sel,

    output alu_ops_t alu_op
);

  typedef enum {
    // setup
    FETCH,
    DECODE,

    // exec
    MEM_ADDR,
    EXEC_R,
    EXEC_I,
    EXEC_U,

    // mem ops
    MEM_READ,
    MEM_WRITE,

    // reg writes
    MEM_WB,
    ALU_WB,

    // misc
    BRANCH,
    JUMP
  } fsm_state_t;

  logic branch_n;
  logic pc_update_n;
  logic inst_en_n;
  logic reg_wren_n;
  logic mem_wren_n;
  mem_addr_sel_t mem_addr_sel_n;
  mem_funct3_sel_t mem_funct3_sel_n;
  alu_src1_sel_t alu_src1_sel_n;
  alu_src2_sel_t alu_src2_sel_n;
  result_sel_t result_sel_n;
  alu_ops_t alu_op_n;

  fsm_state_t state, next_state;


  always_ff @(posedge clk, negedge reset) begin
    if (!reset) begin
      state <= BRANCH;  // any end state so that the outputs for FETCH are correct
      next_state <= FETCH;
    end else state <= next_state;
  end

  // next state
  always_comb begin
    next_state = FETCH;
    case (state)
      FETCH: next_state = DECODE;
      DECODE: begin
        case (opcode)
          `OP_RTYPE: next_state = EXEC_R;
          `OP_ITYPE: next_state = EXEC_I;
          `OP_LUI, `OP_AUIPC: next_state = EXEC_U;
          `OP_LOAD, `OP_STYPE: next_state = MEM_ADDR;
          `OP_BTYPE: next_state = BRANCH;
          `OP_JAL, `OP_JALR: next_state = JUMP;
          default: ;
        endcase
      end
      MEM_ADDR: begin
        case (opcode)
          `OP_LOAD:  next_state = MEM_READ;
          `OP_STYPE: next_state = MEM_WRITE;
          default:   ;
        endcase
      end
      EXEC_R, EXEC_I, EXEC_U, JUMP: next_state = ALU_WB;
      MEM_READ: next_state = MEM_WB;
      MEM_WB, MEM_WRITE, ALU_WB, BRANCH: next_state = FETCH;
      default: ;
    endcase
  end

  // next outputs based on next state
  always_comb begin
    // default - zero it all out unless the state says otherwise
    pc_update_n = 0;
    branch_n = 0;
    inst_en_n = 0;
    reg_wren_n = 0;
    mem_wren_n = 0;
    mem_addr_sel_n = ADDR_PC;
    mem_funct3_sel_n = MEM_FUNCT_DEFINED;
    alu_src1_sel_n = RS1V;
    alu_src2_sel_n = RS2V;
    alu_op_n = ADD_OP;
    result_sel_n = ZERO;

    case (next_state)
      FETCH: begin
        mem_addr_sel_n = ADDR_PC;
        mem_funct3_sel_n = FETCH_INST;
        inst_en_n = 1;
        alu_src1_sel_n = PC;
        alu_src2_sel_n = PC_INC;
        alu_op_n = ADD_OP;
        result_sel_n = ALU_RESULT;
        pc_update_n = 1;
      end
      DECODE: begin
        if (opcode == `OP_JALR) alu_src1_sel_n = RS1V;
        else alu_src1_sel_n = PC_OLD;
        alu_src2_sel_n = IMM;
        alu_op_n = ADD_OP;
      end
      MEM_ADDR: begin
        alu_src1_sel_n = RS1V;
        alu_src2_sel_n = IMM;
        alu_op_n = ADD_OP;
      end
      EXEC_R: begin
        alu_src1_sel_n = RS1V;
        alu_src2_sel_n = RS2V;
        alu_op_n = FUNCT_DEFINED;
      end
      EXEC_I: begin
        alu_src1_sel_n = RS1V;
        alu_src2_sel_n = IMM;
        alu_op_n = FUNCT_DEFINED;
      end
      EXEC_U: begin
        alu_src1_sel_n = RS1V;
        alu_src2_sel_n = IMM;
        alu_op_n = ADD_OP;
      end
      MEM_READ: begin
        result_sel_n   = ALU_CLOCKED;
        mem_addr_sel_n = ADDR_RESULT;
      end
      MEM_WRITE: begin
        result_sel_n = ALU_CLOCKED;
        mem_addr_sel_n = ADDR_RESULT;
        mem_wren_n = 1;
      end
      MEM_WB: begin
        result_sel_n = MEM_RD;
        reg_wren_n   = 1;
      end
      ALU_WB: begin
        result_sel_n = ALU_CLOCKED;
        reg_wren_n   = 1;
      end
      BRANCH: begin
        // Only supports BEQ...
        alu_src1_sel_n = RS1V;
        alu_src2_sel_n = RS2V;
        alu_op_n = SUB_OP;
        branch_n = 1;
      end
      JUMP: begin
        alu_src1_sel_n = PC_OLD;
        alu_src2_sel_n = PC_INC;
        alu_op_n = ADD_OP;
        result_sel_n = ALU_CLOCKED;
        pc_update_n = 1;
      end
      default: ;
    endcase
  end

  // register outputs
  always_ff @(posedge clk or negedge reset) begin
    if (!reset) begin
      branch <= 0;
      pc_update <= 0;
      inst_en <= 0;
      reg_wren <= 0;
      mem_wren <= 0;
      // pick some set of defaults
      mem_addr_sel <= ADDR_PC;
      mem_funct3_sel <= FETCH_INST;
      alu_src1_sel <= RS1V;
      alu_src2_sel <= RS2V;
      result_sel <= ZERO;
      alu_op <= ADD_OP;
    end else begin
      branch <= branch_n;
      pc_update <= pc_update_n;
      inst_en <= inst_en_n;
      reg_wren <= reg_wren_n;
      mem_wren <= mem_wren_n;
      mem_addr_sel <= mem_addr_sel_n;
      mem_funct3_sel <= mem_funct3_sel_n;
      alu_src1_sel <= alu_src1_sel_n;
      alu_src2_sel <= alu_src2_sel_n;
      result_sel <= result_sel_n;
      alu_op <= alu_op_n;
    end
  end

endmodule
