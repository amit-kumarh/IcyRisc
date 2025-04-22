// Immediate Value Generate Module (made up of only immed extender)

module ImmediateGen (
    input logic [24:0] immed,
    input logic [2:0] imm_ctrl,
    output logic signed [31:0] imm_ext
);

  always_comb begin
    case (imm_ctrl)
      ITYPE: begin
        imm_ext = $signed(immed[24:13]);
      end
      STYPE: begin
        imm_ext = $signed({immed[24:18], immed[4:0]});
      end
      BTYPE: begin
        imm_ext = $signed({immed[24], immed[0], immed[23:18], immed[4:1]});
      end
      UTYPE: begin
        imm_ext = immed[24:5] << 12;
      end
      JTYPE: begin
        imm_ext = $signed({immed[24], immed[12:5], immed[13], immed[23:14], 1'b0});
      end
      default: ;
    endcase
  end

endmodule
