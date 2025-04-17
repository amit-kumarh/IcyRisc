import cocotb
import os
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from cocotb.triggers import Timer
from cocotb_tools.runner import get_runner

from pathlib import Path
@cocotb.test()
async def test_ImmediateGen_simple(dut):
    clock = Clock(dut.instr_en, 80, unit="ns")
    cocotb.start_soon(clock.start(start_high=False))

    # initial values
    dut.immed.value = 0b0010101010110100100101011
    dut.imm_ctrl.value = 0

    # check first unsigned values
    await RisingEdge(dut.instr_en)
    assert dut.imm_ext.value == 0b001010101011

    # set new values
    dut.pc.value = 0b0010101010110100100101011
    dut.mem_read_data.value = 1

    # inputs should register just after 1 clock cycle
    await RisingEdge(dut.instr_en)
    await Timer(5, 'ns')
    assert dut.imm_ext.value == 0b001010101011

    # set new values
    dut.pc.value = 0b0010101010110100100101011
    dut.mem_read_data.value = 2

    # inputs should register just after 1 clock cycle
    await RisingEdge(dut.instr_en)
    await Timer(5, 'ns')
    assert dut.imm_ext.value == 0b010101010101

        # set new values
    dut.pc.value = 0b0010101010110100100101011
    dut.mem_read_data.value = 3

    # inputs should register just after 1 clock cycle
    await RisingEdge(dut.instr_en)
    await Timer(5, 'ns')
    assert dut.imm_ext.value == 0b00101010101101001001

        # set new values
    dut.pc.value = 0b0010101010110100100101011
    dut.mem_read_data.value = 4

    # inputs should register just after 1 clock cycle
    await RisingEdge(dut.instr_en)
    await Timer(5, 'ns')
    assert dut.imm_ext.value == 0b001001001


def test_inst_register():
    sim = os.getenv("SIM", "icarus")
    proj_path = Path(__file__).resolve().parent
    sources = list((proj_path.parent / "src").glob("**/*.sv"))
    print(sources)
    runner = get_runner(sim)
    runner.build(
        sources=sources,
        hdl_toplevel="ImmediateGen",
        always=True,
        timescale=("1ns", "1ps")
    )

    runner.test(hdl_toplevel="ImmediateGen", test_module="test_ImmediateGen,",
        timescale=("1ns", "1ps"))

if __name__ == '__main__':
    test_ImmediateGen()
