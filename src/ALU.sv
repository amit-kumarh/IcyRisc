// ALU and its input mutliplexers

module ALU (
    input logic [31:0] PC,
    input logic [31:0] PC_old,
    input logic [31:0] rs1v,
    input logic [31:0] rs2v,
    input logic [31:0] imm_ext,
    input logic [1:0] ALU_src1_sel,
    input logic [1:0] ALU_src2_sel,
    input alu_ctrl_t ALU_ctrl,
    output logic [31:0] ALU_result,
    output logic zero
);

  parameter int INCREMENT = 4;
  logic [31:0] src1_result = 0;
  logic [31:0] src2_result = 0;
  logic [ 4:0] shift_value;

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
        src2_result = INCREMENT;
      end
      2'd3: begin
        src2_result = src2_result;
      end
    endcase
  end

  always_comb begin
    case (ALU_ctrl)
      ADD: begin
        //Return the sum of src1 and 2
        ALU_result = src1_result + src2_result;
      end
      SUB: begin
        //Return the difference between src1 & 2, set zero wire high if they are equal
        ALU_result = src1_result - src2_result;
        if (ALU_result == 0) begin
          zero = 1;
        end
      end
      AND: begin
        //Return a list of bits that is a bit wise and of src1 and 2
        ALU_result = src1_result & src2_result;
      end
      OR: begin
        //Return a list of bits that is a bit wise or of src1 and 2
        ALU_result = src1_result | src2_result;
      end
      XOR: begin
        //Return a list of bits that is a bit wise xor of src1 and 2
        ALU_result = src1_result ^ src2_result;
      end
      SLT: begin
        //Return the lower value of src1 and 2 assuming they are signed
        if ($signed(src1_result) > $signed(src2_result)) begin
          ALU_result = src2_result;
        end else begin
          ALU_result = src1_result;
        end
      end
      SLTU: begin
        //Return the lower value of src1 and 2 assuming they are unsigned
        if (src1_result > src2_result) begin
          ALU_result = src2_result;
        end else begin
          ALU_result = src1_result;
        end
      end
      SLL: begin
        //Shift the src1 value left by a number of bits equal to the lower 5 bits of src2
        shift_value = src2_result[4:0];
        ALU_result  = src1_result << shift_value;
      end
      SRL: begin
        //Shift the src1 value right by a number of bits equal to the lower 5 bits of src2
        shift_value = src2_result[4:0];
        ALU_result  = src1_result >> shift_value;
      end
      SRA: begin
        //Shift the src1 value right by a number of bits equal to the lower 5 bits of src2 and preserve the sign bit
        shift_value = src2_result[4:0];
        ALU_result  = $signed(src1_result) >>> shift_value;
      end
      SRC1: begin
        ALU_result = src1_result;
      end
      SRC2: begin
        ALU_result = src2_result;
      end
      default: ;
    endcase

  end

endmodule

