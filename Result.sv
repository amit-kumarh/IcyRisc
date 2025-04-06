// mux and flip flop of output of ALU

module Result #(

)(
    input logic clk,
    input logic signed ALU_result,
    input logic [31:0] data,
    input logic [1:0] result_sel,
    output logic [31:0] result
);


logic ALU_out [31:0];

always_comb begin
    case (result_sel)
        2'd0: begin
            result <= ALU_out;
        end
        2'd1: begin
            result <= data;
        end
        2'd2: begin
            result <= ALU_result;
        end
        2'd3: begin
            result <= result;
        end
    endcase
end

always_ff @(posedge clk) begin
    ALU_out = ALU_result;
end

endmodule