module inst_register (
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

  always_ff @(posedge inst_en) begin
    inst   <= mem_rd;
    pc_old <= pc;
  end
endmodule
