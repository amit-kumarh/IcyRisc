from logging import LoggerAdapter
import os
from pathlib import Path

import cocotb
import random
from cocotb.clock import Clock
from cocotb.regression import F
from cocotb.triggers import Timer
from cocotb.triggers import RisingEdge, FallingEdge
from cocotb_tools.runner import cocotb_tools, get_runner
from cocotb.types import Array

from constants import *

def assemble_i_instruction(funct3, rd, rs1, imm):
    """Assembles an I-type instruction."""
    return (imm & 0xFFF) << 20 | (rs1 & 0x1F) << 15 | (funct3 & 0x7) << 12 | (rd & 0x1F) << 7 | (OP_ITYPE & 0x7F)

async def initialize_register(dut, reg_index, value):
    """Initializes a specific register in the register file."""
    current_registers = list(dut.reg0.register_file.value)
    current_registers[reg_index] = value
    dut.reg0.register_file.value = Array(current_registers)

async def run_itype_test(dut, inst, reg_index, expected):
    dut.SW.value = 0
    dut.inst.value = inst
    clock = Clock(dut.clk, 80, unit="ns")
    cocotb.start_soon(clock.start(start_high=False))

    # reset registers here
    await RisingEdge(dut.clk)
    dut.SW.value = 1

    await RisingEdge(dut.clk)  # FETCH
    await RisingEdge(dut.clk)  # DECODE
    await RisingEdge(dut.clk)  # EXEC_I
    await RisingEdge(dut.clk)  # ALU_WB
    await RisingEdge(dut.clk)  # FETCH

    await FallingEdge(dut.clk)  # wait a bit so the last cycle registers

    reg = dut.reg0.register_file.value[reg_index]
    print(f"Got {hex(reg)}, Expected {hex(expected)}")
    assert reg == expected


@cocotb.test()
async def test_addi(dut):
    rd = 2
    rs1 = 1
    rs1_val = 0xAABBCCDD
    await initialize_register(dut, rs1, rs1_val)

    imm = 0x000000FF
    inst = assemble_i_instruction(0b000, rd, rs1, imm)
    expected_result = (rs1_val + imm) & 0xFFFFFFFF
    await run_itype_test(dut, inst, rd, expected_result)

@cocotb.test()
async def test_slli(dut):
    """Tests the SLLI instruction."""
    rd = 5
    rs1 = 6
    shamt = 10
    imm = (0b0000000 << 5) | shamt  # funct7 (for SLLI) << 5 | shamt
    inst = assemble_i_instruction(0b001, rd, rs1, imm)
    await initialize_register(dut, rs1, 0x00000005)
    expected_result = (0x00000005 << shamt) & 0xFFFFFFFF
    await run_itype_test(dut, inst, rd, expected_result)

@cocotb.test()
async def test_slti(dut):
    """Tests the SLTI instruction."""
    rd = 7
    rs1 = 8
    imm = -12
    inst = assemble_i_instruction(0b010, rd, rs1, imm)
    await initialize_register(dut, rs1, -15)
    expected_result = 1 if -15 < imm else 0
    await run_itype_test(dut, inst, rd, expected_result)

@cocotb.test()
async def test_sltui(dut):
    """Tests the SLTUI instruction."""
    rd = 9
    rs1 = 10
    imm = 10
    inst = assemble_i_instruction(0b011, rd, rs1, imm)
    await initialize_register(dut, rs1, 5)
    expected_result = 1 if (5 & 0xFFFFFFFF) < (imm & 0xFFFFFFFF) else 0
    await run_itype_test(dut, inst, rd, expected_result)

@cocotb.test()
async def test_xori(dut):
    """Tests the XORI instruction."""
    rd = 11
    rs1 = 12
    imm = 0xFFFFFF0F  # sign extended
    inst = assemble_i_instruction(0b100, rd, rs1, imm)
    await initialize_register(dut, rs1, 0x12345678)
    expected_result = (0x12345678 ^ imm) & 0xFFFFFFFF
    await run_itype_test(dut, inst, rd, expected_result)

@cocotb.test()
async def test_srli(dut):
    """Tests the SRLI instruction."""
    rd = 13
    rs1 = 14
    shamt = 8
    imm = (0b0000000 << 5) | shamt  # funct7 (for SRLI) << 5 | shamt
    inst = assemble_i_instruction(0b101, rd, rs1, imm)
    await initialize_register(dut, rs1, 0x0000FF00)
    expected_result = (0x0000FF00 >> shamt) & 0xFFFFFFFF
    await run_itype_test(dut, inst, rd, expected_result)

@cocotb.test()
async def test_srai(dut):
    """Tests the SRAI instruction."""
    rd = 15
    rs1 = 16
    shamt = 8
    imm = (0b0100000 << 5) | shamt  # funct7 (for SRAI) << 5 | shamt
    inst = assemble_i_instruction(0b101, rd, rs1, imm)
    await initialize_register(dut, rs1, 0xFFFFFE00)  # Negative number
    # shift manually bc python doesn't like 2s complement
    expected_result = 0xFFFFFFFE
    await run_itype_test(dut, inst, rd, expected_result & 0xFFFFFFFF)

@cocotb.test()
async def test_ori(dut):
    """Tests the ORI instruction."""
    rd = 17
    rs1 = 18
    imm = 0x000000F0
    inst = assemble_i_instruction(0b110, rd, rs1, imm)
    await initialize_register(dut, rs1, 0x12340005)
    expected_result = (0x12340005 | imm) & 0xFFFFFFFF
    await run_itype_test(dut, inst, rd, expected_result)

@cocotb.test()
async def test_andi(dut):
    """Tests the ANDI instruction."""
    rd = 19
    rs1 = 20
    imm = 0x000000FF
    inst = assemble_i_instruction(0b111, rd, rs1, imm)
    await initialize_register(dut, rs1, 0xAABBCCDD)
    expected_result = (0xAABBCCDD & imm) & 0xFFFFFFFF
    await run_itype_test(dut, inst, rd, expected_result)

def test_itype():
    sim = os.getenv("SIM", "icarus")
    proj_path = Path(__file__).resolve().parent.parent
    os.environ["PROJ_ROOT"] = str(proj_path)
    sources = str(proj_path / "top.f")

    runner = get_runner(sim)
    runner.build(
        hdl_toplevel="top",
        always=True,
        timescale=("1ns", "1ps"),
        build_args=["-f", sources],
    )

    runner.test(
        hdl_toplevel="top",
        test_module="test_itype,",
        timescale=("1ns", "1ps"),
        hdl_toplevel_lang="verilog",
    )


if __name__ == "__main__":
    test_itype()
