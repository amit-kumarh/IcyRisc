// ALU and its input mutliplexers

module ALU (
    input logic [31:0] PC,
    input logic [31:0] PC_old,
    input logic [4:0] rs1v,
    input logic [4:0] rs2v,
    input logic [31:0] imm_ext,
    input logic [1:0] ALU_src1_sel,
    input logic [1:0] ALU_src2_sel,
    input logic [3:0] ALU_ctrl,
    output logic [31:0] ALU_result,
    output logic zero
);

  parameter increment = 4;
  logic [31:0] src1_result = 0;
  logic [31:0] src2_result = 0;

  always_comb begin
    case (ALU_src1_sel)
      2'd0: begin
        src1_result = PC;
      end
      2'd1: begin
        src1_result = PC_old;
      end
      2'd2: begin
        src1_result = rs1v;
      end
      3'd3: begin
        src1_result = src1_result;
      end
    endcase
  end

  always_comb begin
    case (ALU_src2_sel)
      2'd0: begin
        src2_result = rs2v;
      end
      2'd1: begin
        src2_result = imm_ext;
      end
      2'd2: begin
        src2_result = increment;
      end
      2'd3: begin
        src2_result = src2_result;
      end
    endcase
  end

  always_comb begin
    case (ALU_ctrl)
      4'd0: begin
        //Return the sum of src1 and 2
        ALU_result = src1_result + src2_result;
      end
      4'd1: begin
        //Return the difference between src1 & 2, set zero wire high if they are equal
        ALU_result = src1_result - src2_result;
        if (ALU_result == 0) begin
          zero = 1;
        end
      end
      4'd2: begin
        //Return a list of bits that is a bit wise and of src1 and 2
        ALU_result = src1_result && src2_result;
      end
      4'd3: begin
        //Return a list of bits that is a bit wise or of src1 and 2
        ALU_result = src1_result || src2_result;
      end
      4'd4: begin
        //Return a list of bits that is a bit wise xor of src1 and 2
        ALU_result = (src1_result || src2_result) && ~(src1_result && src2_result);
      end
      4'd5: begin
        //Return the lower value of src1 and 2 assuming they are signed
        if ($signed(src1_result) > $signed(src2_result)) begin
          ALU_result = src2_result;
        end else begin
          ALU_result = src1_result;
        end
      end
      4'd6: begin
        //Return the lower value of src1 and 2 assuming they are unsigned
        if (src1_result > src2_result) begin
          ALU_result = src2_result;
        end else begin
          ALU_result = src1_result;
        end
      end
      4'd7: begin
        //Shift the src1 value left by a number of bits equal to the lower 5 bits of src2
        shift_value = src2_result[4:0];
        ALU_result  = {src1_result[31-shift_value:0], '0};
      end
      4'd8: begin
        //Shift the src1 value right by a number of bits equal to the lower 5 bits of src2
        shift_value = src2_result[4:0];
        ALU_result  = {'0, src1_result[31:shift_value]};
      end
      4'd9: begin
        //Shift the src1 value right by a number of bits equal to the lower 5 bits of src2 and preserve the sign bit
        shift_value = src2_result[4:0];
        ALU_result  = {src1_result[31], '0, src1_result[30:shift_value]};
      end
      4'd10: begin

      end
      4'd11: begin

      end
      4'd12: begin

      end
      4'd13: begin

      end
      4'd14: begin

      end
      4'd15: begin

      end
    endcase

  end

endmodule

