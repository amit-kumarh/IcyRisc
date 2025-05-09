`define OP_ITYPE 19
`define OP_STYPE 7'd35
`define OP_RTYPE 51
`define OP_BTYPE 99

`define OP_LOAD 3
`define OP_AUIPC 23
`define OP_LUI 55
`define OP_JALR 103
`define OP_JAL 111

typedef enum bit [3:0] {
  ADD,
  SUB,
  AND,
  OR,
  XOR,
  SLT,
  SLTU,
  SLL,
  SRL,
  SRA,
  SRC1,
  SRC2
} alu_ctrl_t;

typedef enum bit [2:0] {
  ADD_OP,
  SUB_OP,
  SRC1_OP,  // for LUI
  SRC2_OP,
  SLT_OP,  // for branches
  SLTU_OP,
  FUNCT_DEFINED
} alu_ops_t;

typedef enum bit [1:0] {
  PC,
  PC_OLD,
  RS1V
} alu_src1_sel_t;

typedef enum bit [1:0] {
  RS2V,
  IMM,
  PC_INC
} alu_src2_sel_t;

typedef enum bit [1:0] {
  GREATER,
  EQUAL,
  LESS
} alu_comp_t;

typedef enum bit {
  ADDR_PC,
  ADDR_RESULT
} mem_addr_sel_t;

typedef enum bit {
  FETCH_INST,
  MEM_FUNCT_DEFINED
} mem_funct3_sel_t;

typedef enum bit [1:0] {
  ALU_CLOCKED,
  MEM_RD,
  ALU_RESULT,
  ZERO
} result_sel_t;

typedef enum bit [2:0] {
  ITYPE,
  STYPE,
  BTYPE,
  UTYPE,
  JTYPE
} imm_ctrl_t;

typedef enum bit [2:0] {
  BEQ  = 3'b000,
  BNE  = 3'b001,
  BLT  = 3'b100,
  BGE  = 3'b101,
  BLTU = 3'b110,
  BGEU = 3'b111
} branch_funct3_t;

