`define OP_ITYPE 19
`define OP_STYPE 7'd35
`define OP_RTYPE 51
`define OP_BTYPE 99

`define OP_LOAD 3
`define OP_AUIPC 23
`define OP_LUI 55
`define OP_JALR 103
`define OP_JAL 111

typedef enum {
  ADD,
  SUB,
  AND,
  OR,
  XOR,
  SLT,
  SLTU,
  SLL,
  SRL,
  SRA
} alu_ctrl_t;

typedef enum {
  ADD_OP,
  SUB_OP,
  FUNCT_DEFINED
} alu_ops_t;

typedef enum {
  PC,
  PC_OLD,
  RS1V
} alu_src1_sel_t;

typedef enum {
  RS2V,
  IMM,
  PC_INC
} alu_src2_sel_t;

typedef enum {
  ADDR_PC,
  ADDR_RESULT
} mem_addr_sel_t;

typedef enum {
  ALU_CLOCKED,
  MEM_RD,
  ALU_RESULT
} result_sel_t;

typedef enum {
  ITYPE,
  STYPE,
  BTYPE,
  UTYPE,
  JTYPE
} imm_ctrl_t;

