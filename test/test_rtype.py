import cocotb
import os
from pathlib import Path
import random
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge
from cocotb.types import Array
from cocotb_tools.runner import get_runner

from constants import *


def assemble_r_instruction(funct7, funct3, rd, rs1, rs2):
    """Assembles an R-type instruction."""
    return (funct7 & 0x7F) << 25 | (rs2 & 0x1F) << 20 | (rs1 & 0x1F) << 15 | (funct3 & 0x7) << 12 | (rd & 0x1F) << 7 | (OP_RTYPE & 0x7F)

async def initialize_registers(dut, reg_indexes, values):
    """Initializes a specific register in the register file."""
    current_registers = list(dut.reg0.register_file.value)
    for reg_index, value in zip(reg_indexes, values):
        current_registers[reg_index] = value
    dut.reg0.register_file.value = Array(current_registers)

async def run_rtype_test(dut, inst, rd_index, expected):
    """Runs a single R-type instruction test."""
    dut.SW.value = 0
    dut.inst.value = inst
    clock = Clock(dut.clk, 80, unit="ns")
    cocotb.start_soon(clock.start(start_high=False))

    # Reset registers here
    await RisingEdge(dut.clk)
    dut.SW.value = 1

    await RisingEdge(dut.clk)  # FETCH
    await RisingEdge(dut.clk)  # DECODE
    await RisingEdge(dut.clk)  # EXEC_R
    await RisingEdge(dut.clk)  # ALU_WB
    await RisingEdge(dut.clk)  # FETCH

    await FallingEdge(dut.clk)  # wait a bit so the last cycle registers

    actual_result = dut.reg0.register_file.value[rd_index]
    print(f"Got {hex(actual_result)}, Expected {hex(expected)}")
    assert actual_result == expected

@cocotb.test()
async def test_add(dut):
    """Tests the ADD instruction."""
    rd = 10
    rs1 = 11
    rs2 = 12
    rs1_val = 0x12345678
    rs2_val = 0x87654321
    await initialize_registers(dut, [rs1, rs2], [rs1_val, rs2_val])
    funct7 = 0b0000000
    funct3 = 0b000
    inst = assemble_r_instruction(funct7, funct3, rd, rs1, rs2)
    expected_result = (rs1_val + rs2_val) & 0xFFFFFFFF
    await run_rtype_test(dut, inst, rd, expected_result)

@cocotb.test()
async def test_sub(dut):
    """Tests the SUB instruction."""
    rd = 13
    rs1 = 14
    rs2 = 15
    rs1_val = 0x9ABCDEF0
    rs2_val = 0x12345678
    await initialize_registers(dut, [rs1, rs2], [rs1_val, rs2_val])
    funct7 = 0b0100000
    funct3 = 0b000
    inst = assemble_r_instruction(funct7, funct3, rd, rs1, rs2)
    expected_result = (rs1_val - rs2_val) & 0xFFFFFFFF
    await run_rtype_test(dut, inst, rd, expected_result)

@cocotb.test()
async def test_sll(dut):
    """Tests the SLL instruction."""
    rd = 16
    rs1 = 17
    rs2 = 18
    rs1_val = 0x0000000A
    rs2_val = 5
    await initialize_registers(dut, [rs1, rs2], [rs1_val, rs2_val])
    funct7 = 0b0000000
    funct3 = 0b001
    inst = assemble_r_instruction(funct7, funct3, rd, rs1, rs2)
    expected_result = (rs1_val << (rs2_val & 0x1F)) & 0xFFFFFFFF
    await run_rtype_test(dut, inst, rd, expected_result)

@cocotb.test()
async def test_slt(dut):
    """Tests the SLT instruction."""
    rd = 19
    rs1 = 20
    rs2 = 21
    rs1_val = -5
    rs2_val = 10
    await initialize_registers(dut, [rs1, rs2], [rs1_val, rs2_val])
    funct7 = 0b0000000
    funct3 = 0b010
    inst = assemble_r_instruction(funct7, funct3, rd, rs1, rs2)
    expected_result = 1 if rs1_val < rs2_val else 0
    await run_rtype_test(dut, inst, rd, expected_result)

@cocotb.test()
async def test_sltu(dut):
    """Tests the SLTU instruction."""
    rd = 22
    rs1 = 23
    rs2 = 24
    rs1_val = 0xFFFFFFF0  # Represents a large unsigned number
    rs2_val = 0x0000000A
    await initialize_registers(dut, [rs1, rs2], [rs1_val, rs2_val])
    funct7 = 0b0000000
    funct3 = 0b011
    inst = assemble_r_instruction(funct7, funct3, rd, rs1, rs2)
    expected_result = 1 if (rs1_val & 0xFFFFFFFF) < (rs2_val & 0xFFFFFFFF) else 0
    await run_rtype_test(dut, inst, rd, expected_result)

@cocotb.test()
async def test_xor(dut):
    """Tests the XOR instruction."""
    rd = 25
    rs1 = 26
    rs2 = 27
    rs1_val = 0x12345678
    rs2_val = 0xAABBCCDD
    await initialize_registers(dut, [rs1, rs2], [rs1_val, rs2_val])
    funct7 = 0b0000000
    funct3 = 0b100
    inst = assemble_r_instruction(funct7, funct3, rd, rs1, rs2)
    expected_result = (rs1_val ^ rs2_val) & 0xFFFFFFFF
    await run_rtype_test(dut, inst, rd, expected_result)

@cocotb.test()
async def test_srl(dut):
    """Tests the SRL instruction."""
    rd = 28
    rs1 = 29
    rs2 = 30
    rs1_val = 0xFF000000
    rs2_val = 8
    await initialize_registers(dut, [rs1, rs2], [rs1_val, rs2_val])
    funct7 = 0b0000000
    funct3 = 0b101
    inst = assemble_r_instruction(funct7, funct3, rd, rs1, rs2)
    expected_result = (rs1_val >> (rs2_val & 0x1F)) & 0xFFFFFFFF
    await run_rtype_test(dut, inst, rd, expected_result)

@cocotb.test()
async def test_sra(dut):
    """Tests the SRA instruction."""
    rd = 2
    rs1 = 3
    rs2 = 4
    rs1_val = 0xFFFFFF80  # Negative number
    rs2_val = 4
    await initialize_registers(dut, [rs1, rs2], [rs1_val, rs2_val])
    funct7 = 0b0100000
    funct3 = 0b101
    inst = assemble_r_instruction(funct7, funct3, rd, rs1, rs2)
    expected_result = 0xFFFFFFF8 # do SRA manually bc python is weird
    await run_rtype_test(dut, inst, rd, expected_result & 0xFFFFFFFF)

@cocotb.test()
async def test_or(dut):
    """Tests the OR instruction."""
    rd = 5
    rs1 = 6
    rs2 = 7
    rs1_val = 0x12340000
    rs2_val = 0x000000F0
    await initialize_registers(dut, [rs1, rs2], [rs1_val, rs2_val])
    funct7 = 0b0000000
    funct3 = 0b110
    inst = assemble_r_instruction(funct7, funct3, rd, rs1, rs2)
    expected_result = (rs1_val | rs2_val) & 0xFFFFFFFF
    await run_rtype_test(dut, inst, rd, expected_result)

@cocotb.test()
async def test_and(dut):
    """Tests the AND instruction."""
    rd = 8
    rs1 = 9
    rs2 = 10
    rs1_val = 0xAABBCCDD
    rs2_val = 0x000000FF
    await initialize_registers(dut, [rs1, rs2], [rs1_val, rs2_val])
    funct7 = 0b0000000
    funct3 = 0b111
    inst = assemble_r_instruction(funct7, funct3, rd, rs1, rs2)
    expected_result = (rs1_val & rs2_val) & 0xFFFFFFFF
    await run_rtype_test(dut, inst, rd, expected_result)

def test_rtype():
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
        test_module="test_rtype",
        timescale=("1ns", "1ps"),
        hdl_toplevel_lang="verilog",
    )

if __name__ == "__main__":
    test_rtype()
