module program_counter #(
    parameter PROGRAM_START = 9'h100
) (
    input logic reset,
    input logic [31:0] pc_next,
    input logic pc_en,
    output logic [31:0] pc
);
  always_ff @(posedge pc_en, posedge reset) begin
    if (reset) begin
      pc <= PROGRAM_START;
    end else begin
      pc <= pc_next;
    end
  end
endmodule
