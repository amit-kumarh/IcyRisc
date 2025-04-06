// ALU and its input mutliplexers

module ALU #(

)(
    input logic [31:0] PC,
    input logic [31:0] PC_old,
    input logic [4:0] rs1v,
    input logic [4:0] rs2v,
    input logic [31:0] imm_ext,
    input logic [1:0] ALU_src1_sel,
    input logic [1:0] ALU_src2_sel,
    input logic [] ALU_ctrl,
    output logic [31:0] ALU_result
);

parameter increment = 4;
logic [31:0] src1_result = 0;
logic [31:0] src2_result = 0;

always_comb begin
    case (ALU_src1_sel)
        2'd0: begin
            src1_result <= PC;
        end
        2'd1: begin
            src1_result <= PC_old;
        end
        2'd2: begin
            src1_result <= rs1v;
        end
        3'd3: begin
            src1_result <= src1_result;
        end
    endcase
end

always_comb begin
    case (ALU_src2_sel)
        2'd0: begin
           src2_result <= rs2v; 
        end
        2'd1: begin
            src2_result <= imm_ext;
        end 
        2'd2: begin
            src2_result <= increment;
        end
        2'd3: begin
            src2_result <= src2_result;
        end
    endcase
end


endmodule