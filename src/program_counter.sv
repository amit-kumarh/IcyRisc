module program_counter #(
    parameter PROGRAM_START = 32'd0
) (
    input logic reset,
    input logic [31:0] pc_next,
    input logic pc_en,
    output logic [31:0] pc
);
  always_ff @(posedge pc_en, negedge reset) begin
    if (!reset) begin
      pc <= PROGRAM_START;
    end else begin
      pc <= pc_next;
    end
  end
endmodule
