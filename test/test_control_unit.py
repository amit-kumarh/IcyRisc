from logging import LoggerAdapter
import os
from pathlib import Path

import cocotb
import random
from cocotb.clock import Clock
from cocotb.regression import F
from cocotb.triggers import Timer
from cocotb.triggers import RisingEdge, FallingEdge
from cocotb_tools.runner import get_runner

from constants import *

ADD_RTYPE = 0x00418133 # add x2, x3, x4
ADDI = 0x02f18113 # addi x2, x3, 47
LW = 0x02f1a103 # lw x2, 47(x3)
JALR = 0x02f18167 # jalr x2, 47(x3)
SW = 0x0221a7a3 # sw x2, 47(x3)
BEQ = 0x02310763 # beq x2, x3, 47
LUI = 0x0002f137 # lui x2, 47
AUIPC = 0x0002f117 # auipc x2, 47
JAL = 0x02e0016f # jal x2, 47

LANGUAGE = os.getenv("HDL_TOPLEVEL_LANG", "verilog").lower().strip()

@cocotb.test()
async def test_lw(dut):
    dut.reset.value = 0
    dut.inst.value = LW
    clock = Clock(dut.clk, 80, unit="ns")
    cocotb.start_soon(clock.start(start_high=False))

    # reset registers here
    await RisingEdge(dut.clk)
    dut.reset.value = 1

    # start of FETCH
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    # verify FETCH
    assert dut.f0.state.value == FETCH
    assert dut.mem_addr_sel.value == ADDR_PC
    assert dut.inst_en.value
    assert dut.alu_src1_sel.value == PC
    assert dut.alu_src2_sel.value == PC_INC
    assert dut.alu_ctrl.value == ADD
    assert dut.result_sel.value == ALU_RESULT
    assert dut.pc_en.value

    # verify DECODE
    await FallingEdge(dut.clk)
    assert dut.f0.state.value == DECODE

    # verify MEM_ADDR
    await FallingEdge(dut.clk)
    assert dut.f0.state.value == MEM_ADDR
    assert dut.alu_src1_sel.value == RS1V
    assert dut.alu_src2_sel.value == IMM
    assert dut.alu_ctrl.value == ADD

    # verify MEM_READ
    await FallingEdge(dut.clk)
    assert dut.f0.state.value == MEM_READ
    assert dut.result_sel.value == ALU_CLOCKED
    assert dut.mem_addr_sel.value == ADDR_RESULT

    # verify MEM_WB
    await FallingEdge(dut.clk)
    assert dut.f0.state.value == MEM_WB
    assert dut.result_sel.value == MEM_RD
    assert dut.reg_wren.value

    await FallingEdge(dut.clk)
    assert dut.f0.state.value == FETCH

@cocotb.test()
async def test_sw(dut):
    dut.reset.value = 0
    dut.inst.value = SW
    clock = Clock(dut.clk, 80, unit="ns")
    cocotb.start_soon(clock.start(start_high=False))

    # reset registers here
    await RisingEdge(dut.clk)
    dut.reset.value = 1

    # start of FETCH
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    # verify FETCH
    assert dut.f0.state.value == FETCH
    assert dut.mem_addr_sel.value == ADDR_PC
    assert dut.inst_en.value
    assert dut.alu_src1_sel.value == PC
    assert dut.alu_src2_sel.value == PC_INC
    assert dut.alu_ctrl.value == ADD
    assert dut.result_sel.value == ALU_RESULT
    assert dut.pc_en.value

    # verify DECODE
    await FallingEdge(dut.clk)
    assert dut.f0.state.value == DECODE

    # verify MEM_ADDR
    await FallingEdge(dut.clk)
    assert dut.f0.state.value == MEM_ADDR
    assert dut.alu_src1_sel.value == RS1V
    assert dut.alu_src2_sel.value == IMM
    assert dut.alu_ctrl.value == ADD

    # verify MEM_WRITE
    await FallingEdge(dut.clk)
    assert dut.f0.state.value == MEM_WRITE
    assert dut.result_sel.value == ALU_CLOCKED
    assert dut.mem_addr_sel.value == ADDR_RESULT
    assert dut.mem_wren.value

    # back to FETCH
    await FallingEdge(dut.clk)
    assert dut.f0.state.value == FETCH

@cocotb.test()
async def test_itype(dut):
    dut.reset.value = 0
    dut.inst.value = ADDI
    clock = Clock(dut.clk, 80, unit="ns")
    cocotb.start_soon(clock.start(start_high=False))

    # reset registers here
    await RisingEdge(dut.clk)
    dut.reset.value = 1

    # start of FETCH
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    # verify FETCH
    assert dut.f0.state.value == FETCH
    assert dut.mem_addr_sel.value == ADDR_PC
    assert dut.inst_en.value
    assert dut.alu_src1_sel.value == PC
    assert dut.alu_src2_sel.value == PC_INC
    assert dut.alu_ctrl.value == ADD
    assert dut.result_sel.value == ALU_RESULT
    assert dut.pc_en.value

    # verify DECODE
    await FallingEdge(dut.clk)
    assert dut.f0.state.value == DECODE

    # verify EXEC_I
    await FallingEdge(dut.clk)
    assert dut.f0.state.value == EXEC_I
    assert dut.alu_src1_sel.value == RS1V
    assert dut.alu_src2_sel.value == IMM
    assert dut.alu_ctrl.value == ADD

    # verify ALU_WB
    await FallingEdge(dut.clk)
    assert dut.f0.state.value == ALU_WB
    assert dut.result_sel.value == ALU_CLOCKED
    assert dut.reg_wren.value

    # back to FETCH
    await FallingEdge(dut.clk)
    assert dut.f0.state.value == FETCH

@cocotb.test()
async def test_rtype(dut):
    dut.reset.value = 0
    dut.inst.value = ADD_RTYPE
    clock = Clock(dut.clk, 80, unit="ns")
    cocotb.start_soon(clock.start(start_high=False))

    # reset registers here
    await RisingEdge(dut.clk)
    dut.reset.value = 1

    # start of FETCH
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    # verify FETCH
    assert dut.f0.state.value == FETCH
    assert dut.mem_addr_sel.value == ADDR_PC
    assert dut.inst_en.value
    assert dut.alu_src1_sel.value == PC
    assert dut.alu_src2_sel.value == PC_INC
    assert dut.alu_ctrl.value == ADD
    assert dut.result_sel.value == ALU_RESULT
    assert dut.pc_en.value

    # verify DECODE
    await FallingEdge(dut.clk)
    assert dut.f0.state.value == DECODE

    # verify EXEC_R
    await FallingEdge(dut.clk)
    assert dut.f0.state.value == EXEC_R
    assert dut.alu_src1_sel.value == RS1V
    assert dut.alu_src2_sel.value == RS2V
    assert dut.alu_ctrl.value == ADD

    # verify ALU_WB
    await FallingEdge(dut.clk)
    assert dut.f0.state.value == ALU_WB
    assert dut.result_sel.value == ALU_CLOCKED
    assert dut.reg_wren.value

    # back to FETCH
    await FallingEdge(dut.clk)
    assert dut.f0.state.value == FETCH

@cocotb.test()
async def test_jal(dut):
    dut.reset.value = 0
    dut.inst.value = JAL
    clock = Clock(dut.clk, 80, unit="ns")
    cocotb.start_soon(clock.start(start_high=False))

    # reset registers here
    await RisingEdge(dut.clk)
    dut.reset.value = 1

    # start of FETCH
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    # verify FETCH
    assert dut.f0.state.value == FETCH
    assert dut.mem_addr_sel.value == ADDR_PC
    assert dut.inst_en.value
    assert dut.alu_src1_sel.value == PC
    assert dut.alu_src2_sel.value == PC_INC
    assert dut.alu_ctrl.value == ADD
    assert dut.result_sel.value == ALU_RESULT
    assert dut.pc_en.value

    # verify DECODE
    await FallingEdge(dut.clk)
    assert dut.f0.state.value == DECODE
    assert dut.alu_src1_sel.value == PC_OLD
    assert dut.alu_src2_sel.value == IMM
    assert dut.alu_ctrl.value == ADD

    # verify JUMP
    await FallingEdge(dut.clk)
    assert dut.f0.state.value == JUMP
    assert dut.alu_src1_sel.value == PC_OLD
    assert dut.alu_src2_sel.value == PC_INC
    assert dut.alu_ctrl.value == ADD
    assert dut.result_sel.value == ALU_CLOCKED
    assert dut.pc_en.value

    # verify ALU_WB
    await FallingEdge(dut.clk)
    assert dut.f0.state.value == ALU_WB
    assert dut.result_sel.value == ALU_CLOCKED
    assert dut.reg_wren.value

    # back to FETCH
    await FallingEdge(dut.clk)
    assert dut.f0.state.value == FETCH

@cocotb.test()
async def test_beq(dut):
    dut.reset.value = 0
    dut.inst.value = BEQ
    dut.alu_zero.value = 1
    clock = Clock(dut.clk, 80, unit="ns")
    cocotb.start_soon(clock.start(start_high=False))

    # reset registers here
    await RisingEdge(dut.clk)
    dut.reset.value = 1

    # start of FETCH
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    # verify FETCH
    assert dut.f0.state.value == FETCH
    assert dut.mem_addr_sel.value == ADDR_PC
    assert dut.inst_en.value
    assert dut.alu_src1_sel.value == PC
    assert dut.alu_src2_sel.value == PC_INC
    assert dut.alu_ctrl.value == ADD
    assert dut.result_sel.value == ALU_RESULT
    assert dut.pc_en.value

    # verify DECODE
    await FallingEdge(dut.clk)
    assert dut.f0.state.value == DECODE
    assert dut.alu_src1_sel.value == PC_OLD
    assert dut.alu_src2_sel.value == IMM
    assert dut.alu_ctrl.value == ADD

    # verify BRANCH
    await FallingEdge(dut.clk)
    assert dut.f0.state.value == BRANCH
    assert dut.alu_src1_sel.value == RS1V
    assert dut.alu_src2_sel.value == RS2V
    assert dut.alu_ctrl.value == SUB
    assert dut.result_sel.value == ALU_CLOCKED
    assert dut.branch.value
    assert dut.pc_en.value

    # back to FETCH
    await FallingEdge(dut.clk)
    assert dut.f0.state.value == FETCH

@cocotb.test()
async def test_alu_decoder(dut):
    dut.reset.value = 1
    dut.inst.value = 0
    clock = Clock(dut.clk, 80, unit="ns")
    cocotb.start_soon(clock.start(start_high=False))

    ## CONTROLLER DEFINED
    dut.ad0.alu_op.value = 0 # add
    await RisingEdge(dut.clk)
    assert dut.alu_ctrl.value == ADD

    dut.ad0.alu_op.value = 1 # sub
    await RisingEdge(dut.clk)
    assert dut.alu_ctrl.value == SUB

    # FUNCT_DEFINED
    dut.ad0.alu_op.value = FUNCT_DEFINED

    # add/sub
    dut.ad0.funct3.value = 0b000
    dut.ad0.op_5.value = 0 # addi
    await RisingEdge(dut.clk)
    assert dut.alu_ctrl.value == ADD

    dut.ad0.op_5.value = 1 # add
    await RisingEdge(dut.clk)
    assert dut.alu_ctrl.value == ADD

    dut.ad0.op_5.value = 1 # sub
    dut.ad0.funct7_5.value = 1
    await RisingEdge(dut.clk)
    assert dut.alu_ctrl.value == SUB

    dut.ad0.funct3.value = 0b111 # AND
    await RisingEdge(dut.clk)
    assert dut.alu_ctrl.value == AND

    dut.ad0.funct3.value = 0b110 # OR
    await RisingEdge(dut.clk)
    assert dut.alu_ctrl.value == OR

    dut.ad0.funct3.value = 0b100 # XOR
    await RisingEdge(dut.clk)
    assert dut.alu_ctrl.value == XOR

    dut.ad0.funct3.value = 0b010 # SLT
    await RisingEdge(dut.clk)
    assert dut.alu_ctrl.value == SLT

    dut.ad0.funct3.value = 0b011 # SLTU
    await RisingEdge(dut.clk)
    assert dut.alu_ctrl.value == SLTU

    dut.ad0.funct3.value = 0b001 # SLL
    await RisingEdge(dut.clk)
    assert dut.alu_ctrl.value == SLL

    dut.ad0.funct3.value = 0b101 # SRL
    dut.ad0.funct7_5.value = 0
    await RisingEdge(dut.clk)
    assert dut.alu_ctrl.value == SRL

    dut.ad0.funct3.value = 0b101 # SRA
    dut.ad0.funct7_5.value = 1
    await RisingEdge(dut.clk)
    assert dut.alu_ctrl.value == SRA

@cocotb.test()
async def test_imm_decoder(dut):
    dut.reset.value = 1
    clock = Clock(dut.clk, 80, unit="ns")
    cocotb.start_soon(clock.start(start_high=False))

    # ITYPE
    dut.inst.value = ADDI
    await RisingEdge(dut.clk)
    assert dut.imm_ctrl.value == ITYPE

    dut.inst.value = LW
    await RisingEdge(dut.clk)
    assert dut.imm_ctrl.value == ITYPE

    dut.inst.value = JALR
    await RisingEdge(dut.clk)
    assert dut.imm_ctrl.value == ITYPE

    # STYPE
    dut.inst.value = SW
    await RisingEdge(dut.clk)
    assert dut.imm_ctrl.value == STYPE

    # BTYPE
    dut.inst.value = BEQ
    await RisingEdge(dut.clk)
    assert dut.imm_ctrl.value == BTYPE

    # UTYPE
    dut.inst.value = LUI
    await RisingEdge(dut.clk)
    assert dut.imm_ctrl.value == UTYPE

    dut.inst.value = AUIPC
    await RisingEdge(dut.clk)
    assert dut.imm_ctrl.value == UTYPE

    # JTYPE
    dut.inst.value = JAL
    await RisingEdge(dut.clk)
    assert dut.imm_ctrl.value == JTYPE

def test_control_unit():
    sim = os.getenv("SIM", "icarus")
    proj_path = Path(__file__).resolve().parent
    sources = list((proj_path.parent / "src" / "control").glob("*.sv"))
    runner = get_runner(sim)
    runner.build(
        sources=sources,
        hdl_toplevel="control",
        always=True,
        timescale=("1ns", "1ps")
    )

    runner.test(hdl_toplevel="control", test_module="test_control_unit,",
        timescale=("1ns", "1ps"))

if __name__ == '__main__':
    test_control_unit()
