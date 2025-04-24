import os
from pathlib import Path

import cocotb
import random
from cocotb.clock import Clock
from cocotb.triggers import Timer
from cocotb.triggers import RisingEdge, FallingEdge
from cocotb_tools.runner import get_runner

LANGUAGE = os.getenv("HDL_TOPLEVEL_LANG", "verilog").lower().strip()

@cocotb.test()
async def test_reset(dut):
    dut.reset.value = 0
    clock = Clock(dut.pc_en, 80, unit="ns")
    cocotb.start_soon(clock.start(start_high=False))
    await RisingEdge(dut.pc_en)
    await FallingEdge(dut.pc_en)
    dut.reset.value = 1
    assert dut.pc.value == 0x000

@cocotb.test()
async def test_pc_next(dut):
    dut.reset.value = 1
    dut.pc_next.value = 0
    dut.pc_en.value = 1

    clock = Clock(dut.clk, 80, unit="ns")
    cocotb.start_soon(clock.start(start_high=False))

    # Synchronize with the clock. This will regisiter the initial `d` value
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    assert dut.pc.value == 0

    dut.pc_next.value = 1

    await FallingEdge(dut.clk)
    assert dut.pc.value == 1

def test_program_counter():
    sim = os.getenv("SIM", "icarus")
    proj_path = Path(__file__).resolve().parent
    sources = list((proj_path.parent / "src").glob("program_counter.sv"))
    runner = get_runner(sim)
    runner.build(
        sources=sources,
        hdl_toplevel="program_counter",
        always=True,
        timescale=("1ns", "1ps")
    )

    runner.test(hdl_toplevel="program_counter", test_module="test_program_counter,",
        timescale=("1ns", "1ps"))

if __name__ == '__main__':
    test_program_counter()
