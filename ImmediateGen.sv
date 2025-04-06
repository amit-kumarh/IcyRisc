// Immediate Value Generate Module (made up of only immed extender)

module ImmediateGen #(


)(
    input logic immed[24:0],
    input logic imm_ctrl[2:0],
    output logic signed imm_ext[31:0]

)

always_comb begin
    case (imm_ctrl) 
        3'd0: begin
            imm_ext <= $signed(immed[24:13]);
        end
        3'd1: begin
            imm_ext <= $signed(immed[24:18, 4:0]);
        end
        3'd2: begin
            imm_ext <= $signed(immed[24, 0, 23:18, 4:1]);
        end
        3'd3: begin
            imm_ext <= $signed(immed[24:5]);
        end
        3'd4: begin
            imm_ext <= $signed(immed[24, 12:5, 13, 23:14]);
        end
        3'd5: begin

        end
        3'd6: begin

        end
        3'd7: begin

        end 

    endcase
end

endmodule