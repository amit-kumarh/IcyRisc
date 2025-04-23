module inst_register (
    input logic clk,
    input logic [31:0] pc,
    input logic [31:0] mem_rd,
    input logic inst_en,
    output logic [31:0] inst,
    output logic [31:0] pc_old
);
  initial begin
    inst   = 0;
    pc_old = 0;
  end

  // sample on negedge in case we're coming out of a jump/branch
  // so mem_rd has time to update
  always_ff @(negedge clk) begin
    if (inst_en) begin
      inst   <= mem_rd;
      pc_old <= pc;
    end
  end
endmodule
