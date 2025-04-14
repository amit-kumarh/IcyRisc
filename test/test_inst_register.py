import cocotb
import os
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from cocotb.triggers import Timer
from cocotb_tools.runner import get_runner

from pathlib import Path
@cocotb.test()
async def test_inst_register_simple(dut):
    clock = Clock(dut.instr_en, 80, unit="ns")
    cocotb.start_soon(clock.start(start_high=False))

    # initial values
    dut.pc.value = 0
    dut.mem_read_data.value = 0

    # check initial values
    await RisingEdge(dut.instr_en)
    assert dut.instr.value == 0
    assert dut.pc_old.value == 0

    # set new values
    dut.pc.value = 1
    dut.mem_read_data.value = 2

    # inputs should register just after 1 clock cycle
    await RisingEdge(dut.instr_en)
    await Timer(5, 'ns')
    assert dut.pc_old.value == 1
    assert dut.instr.value == 2

def test_inst_register():
    sim = os.getenv("SIM", "icarus")
    proj_path = Path(__file__).resolve().parent
    sources = list((proj_path.parent / "src").glob("**/*.sv"))
    print(sources)
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
