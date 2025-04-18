module top (
    input logic clk,

    input  logic SW,
    output logic RGB_R,
    output logic RGB_G,
    output logic RGB_B,
    output logic LED
);
  logic [31:0] mem_rd;
  logic [31:0] mem_rd_clocked;

  logic pc_en;
  logic inst_en;
  logic reg_wren;
  logic mem_wren;
  imm_ctrl_t imm_ctrl;
  alu_ctrl_t alu_ctrl;
  mem_addr_sel_t mem_addr_sel;
  mem_funct3_sel_t mem_funct3_sel;
  alu_src1_sel_t alu_src1_sel;
  alu_src2_sel_t alu_src2_sel;
  result_sel_t result_sel;

  logic [31:0] pc;
  logic [31:0] pc_old;
  logic [31:0] inst;

  logic [31:0] rs1v;
  logic [31:0] rs2v;

  logic [31:0] imm_ext;

  logic alu_zero;
  logic [31:0] alu_result;

  logic [31:0] result;

  logic red, green, blue, led;

  control c0 (
      .reset(SW),
      .clk  (clk),
      .inst (inst),

      .pc_en(pc_en),
      .inst_en(inst_en),
      .reg_wren(reg_wren),
      .mem_wren(mem_wren),

      .imm_ctrl(imm_ctrl),
      .alu_ctrl(alu_ctrl),

      .mem_addr_sel(mem_addr_sel),
      .mem_funct3_sel(mem_funct3_sel),
      .alu_src1_sel(alu_src1_sel),
      .alu_src2_sel(alu_src2_sel),
      .result_sel(result_sel)
  );

  ALU alu0 (
      .PC(pc),
      .PC_old(pc_old),
      .rs1v(rs1v),
      .rs2v(rs2v),
      .imm_ext(imm_ext),

      .ALU_src1_sel(alu_src1_sel),
      .ALU_src2_sel(alu_src2_sel),
      .ALU_ctrl(alu_ctrl),

      .ALU_result(alu_result),
      .zero(alu_zero)
  );

  Register reg0 (
      .clk(clk),
      .rs1(inst[19:15]),
      .rs2(inst[24:20]),
      .wd_reg(inst[11:7]),
      .wdv(result),
      .wren(reg_wren),

      .rs1v(rs1v),
      .rs2v(rs2v)
  );

  ImmediateGen imm0 (
      .immed(inst[31:7]),
      .imm_ctrl(imm_ctrl),
      .imm_ext(imm_ext)
  );

  Result r0 (
      .clk(clk),
      .ALU_result(alu_result),
      .data(mem_rd_clocked),
      .result_sel(result_sel),
      .result(result)
  );

  program_counter p0 (
      .clk(clk),
      .reset(SW),
      .pc_next(result),
      .pc_en(pc_en),
      .pc(pc)
  );

  inst_register i0 (
      .pc(pc),
      .mem_rd(mem_rd),
      .inst_en(inst_en),
      .inst(inst),
      .pc_old(pc_old)
  );

  // address mux
  logic [31:0] mem_addr;
  always_comb begin
    case (mem_addr_sel)
      ADDR_PC: mem_addr = pc;
      ADDR_RESULT: mem_addr = result;
      default: mem_addr = 0;
    endcase
  end

  // address mux
  logic [2:0] mem_funct3;
  always_comb begin
    case (mem_funct3_sel)
      FETCH_INST: mem_funct3 = 3'b010;
      default: mem_funct3 = inst[14:12];
    endcase
  end

  memory #(
      .INIT_FILE("programs/rv32i_test")
  ) mem0 (
      .clk(clk),
      .write_mem(mem_wren),
      .funct3(mem_funct3),
      .write_address(mem_addr),
      .write_data(rs2v),
      .read_address(mem_addr),

      .read_data(mem_rd),
      .read_data_clocked(mem_rd_clocked),

      .led  (led),
      .red  (red),
      .green(green),
      .blue (blue)
  );

  assign LED   = ~led;
  assign RGB_R = ~red;
  assign RGB_G = ~green;
  assign RGB_B = ~blue;

endmodule
