module instRegister #(
) (
    input logic [31:0] pc,
    input logic [31:0] mem_read_data,
    input logic instr_en,
    output logic [31:0] instr,
    output logic [31:0] pc_old
);
  always_ff @(posedge instr_en) begin
    intsr  <= mem_read_data;
    pc_old <= pc;
  end
endmodule
