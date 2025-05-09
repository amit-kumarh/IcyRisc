import cocotb
import os
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge
from cocotb.triggers import Timer
from cocotb_tools.runner import get_runner

from pathlib import Path
@cocotb.test()
async def test_inst_register_simple(dut):
    dut.inst_en.value = 1
    clock = Clock(dut.clk, 80, unit="ns")
    cocotb.start_soon(clock.start(start_high=False))

    # initial values
    dut.pc.value = 0
    dut.mem_rd.value = 0

    # check initial values
    await RisingEdge(dut.clk)
    assert dut.inst.value == 0
    assert dut.pc_old.value == 0

    # set new values
    dut.pc.value = 1
    dut.mem_rd.value = 2

    # inputs should register just after 1 clock cycle
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    assert dut.pc_old.value == 1
    assert dut.inst.value == 2

def test_inst_register():
    sim = os.getenv("SIM", "icarus")
    proj_path = Path(__file__).resolve().parent
    sources = list((proj_path.parent / "src").glob("inst_register.sv"))
    runner = get_runner(sim)
    runner.build(
        sources=sources,
        hdl_toplevel="inst_register",
        always=True,
        timescale=("1ns", "1ps")
    )

    runner.test(hdl_toplevel="inst_register", test_module="test_inst_register,",
        timescale=("1ns", "1ps"))

if __name__ == '__main__':
    test_inst_register()
