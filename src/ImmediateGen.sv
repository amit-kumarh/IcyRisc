// Immediate Value Generate Module (made up of only immed extender)

module ImmediateGen (
    input logic [24:0] immed,
    input logic [2:0] imm_ctrl,
    output logic signed [31:0] imm_ext
);

  always_comb begin
    case (imm_ctrl)
      3'd0: begin
        imm_ext = $signed(immed[24:13]);
      end
      3'd1: begin
        imm_ext = $signed({immed[24:18], immed[4:0]});
      end
      3'd2: begin
        imm_ext = $signed({immed[24], immed[0], immed[23:18], immed[4:1]});
      end
      3'd3: begin
        imm_ext = $signed(immed[24:5]);
      end
      3'd4: begin
        imm_ext = $signed({immed[24], immed[12:5], immed[13], immed[23:14]});
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
