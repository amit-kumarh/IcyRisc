import os
from pathlib import Path

import cocotb
import random
from cocotb.clock import Clock
from cocotb.triggers import Timer
from cocotb.triggers import RisingEdge
from cocotb_tools.runner import get_runner

LANGUAGE = os.getenv("HDL_TOPLEVEL_LANG", "verilog").lower().strip()

@cocotb.test()
async def test_reset(dut):
    dut.reset.value = 1
    await Timer(80, 'ns')
    dut.reset.value = 0
    await Timer(80, 'ns')
    assert dut.pc.value == 0x100

@cocotb.test()
async def test_pc_next(dut):
    dut.reset.value = 1
    dut.pc_next.value = 0

    clock = Clock(dut.pc_en, 80, unit="ns")
    cocotb.start_soon(clock.start(start_high=False))

    # Synchronize with the clock. This will regisiter the initial `d` value
    await RisingEdge(dut.pc_en)
    expected_val = 0  # Matches initial input value
    for i in range(10):
        val = random.randint(0, 2**32)
        dut.pc_next.value = val  # Assign the random value val to the input port d
        await RisingEdge(dut.pc_en)
        assert dut.pc.value == expected_val, f"output q was incorrect on the {i}th cycle"
        expected_val = val  # Save random value for next RisingEdge

    # Check the final input on the next clock
    await RisingEdge(dut.pc_en)
    assert dut.pc.value == expected_val, "output q was incorrect on the last cycle"

def test_program_counter():
    sim = os.getenv("SIM", "icarus")
    proj_path = Path(__file__).resolve().parent
    sources = list((proj_path.parent / "src").glob("**/*.sv"))
    print(sources)
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
