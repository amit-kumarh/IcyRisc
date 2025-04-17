module program_counter #(
    parameter PROGRAM_START = 32'd0
) (
    input logic clk,
    input logic reset,
    input logic [31:0] pc_next,
    input logic pc_en,
    output logic [31:0] pc
);
  always_ff @(posedge clk, negedge reset) begin
    if (!reset) begin
      pc <= PROGRAM_START;
    end else if (pc_en) begin
      pc <= pc_next;
    end
  end
endmodule
