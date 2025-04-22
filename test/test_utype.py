# test_utype.py
import cocotb
import os
from pathlib import Path
import random
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge
from cocotb.types import Array
from cocotb_tools.runner import get_runner

from constants import *

def assemble_u_instruction(opcode, rd, imm):
    """Assembles a U-type instruction."""
    return (imm & 0xFFFFF) << 12 | (rd & 0x1F) << 7 | (opcode & 0x7F)

async def initialize_register(dut, reg_index, value):
    """Initializes a specific register in the register file."""
    current_registers = list(dut.reg0.register_file.value)
    current_registers[reg_index] = value
    dut.reg0.register_file.value = Array(current_registers)

async def run_utype_test(dut, inst, rd_index, expected):
    """Runs a single U-type instruction test."""
    dut.SW.value = 0
    dut.inst.value = inst
    clock = Clock(dut.clk, 80, unit="ns")
    cocotb.start_soon(clock.start(start_high=False))

    # Reset registers here
    await RisingEdge(dut.clk)
    dut.SW.value = 1

    await RisingEdge(dut.clk)  # FETCH
    await RisingEdge(dut.clk)  # DECODE
    await RisingEdge(dut.clk)  # EXEC_{U} (auipc or lui)
    await RisingEdge(dut.clk)  # ALU_WB
    await RisingEdge(dut.clk)  # FETCH

    await FallingEdge(dut.clk)  # wait a bit so the last cycle registers

    actual_result = dut.reg0.register_file.value[rd_index]
    print(f"Got {hex(actual_result)}, Expected {hex(expected)}")
    assert actual_result == expected

@cocotb.test()
async def test_lui(dut):
    """Tests the LUI (Load Upper Immediate) instruction."""
    rd = 10
    imm = 0xABCDE
    inst = assemble_u_instruction(OP_LUI, rd, imm)
    expected_result = (imm << 12) & 0xFFFFFFFF
    await run_utype_test(dut, inst, rd, expected_result)

@cocotb.test()
async def test_auipc(dut):
    """Tests the AUIPC (Add Upper Immediate to PC) instruction."""
    rd = 15
    imm = 0x12345
    inst = assemble_u_instruction(OP_AUIPC, rd, imm)

    # PC is set to 0 on reset
    pc_at_exec = 0x00000000
    expected_result = (pc_at_exec + (imm << 12)) & 0xFFFFFFFF

    await run_utype_test(dut, inst, rd, expected_result)

def test_utype():
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
        test_module="test_utype",
        timescale=("1ns", "1ps"),
        hdl_toplevel_lang="verilog",
    )

if __name__ == "__main__":
    test_utype()
