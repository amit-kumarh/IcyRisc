module programCounter #(
) (
    input logic reset,
    input logic [31:0] pc_next,
    input logic pc_en,
    output logic [31:0] pc
);
  always_ff @(posedge pc_en, posedge reset) begin
    if (reset) begin
      pc <= 13'h1000;
    end else begin
      pc <= pc_next;
    end
  end
endmodule
