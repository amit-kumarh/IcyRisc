import cocotb
import os
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from cocotb.triggers import Timer
from cocotb_tools.runner import get_runner

from pathlib import Path
@cocotb.test()
async def test_alu_simple(dut):
    clock = Clock(dut.inst_en, 80, unit="ns")
    cocotb.start_soon(clock.start(start_high=False))

    # initial values
    dut.PC.value = 0
    dut.PC_old.value = 0
    dut.rs1v.value = 0
    dut.rs2v.value = 0
    dut.imm_ext.value = 0
    dut.ALU_src1_sel.value = 0
    dut.ALU_scr2_sel.value = 0
    dut.ALU_ctrl = 0

    # check initial values
    await RisingEdge(dut.inst_en)
    assert dut.ALU_result.value == 0
    assert dut.ALU_comp.value == 0


    # set new values
    dut.PC.value = 25
    dut.rs2v.value = 2


    # inputs should register just after 1 clock cycle
    await RisingEdge(dut.inst_en)
    await Timer(5, 'ns')
    assert dut.ALU_result.value == 27
    assert dut.ALU_comp.value == 0

     # set new values
    dut.PC_old.value = 50
    dut.imm_ext.value = 8
    dut.ALU_src1_sel.value = 1
    dut.ALU_src2_sel.value = 1
    dut.ALU_ctrl.value = 1


    # inputs should register just after 1 clock cycle
    await RisingEdge(dut.inst_en)
    await Timer(5, 'ns')
    assert dut.ALU_result.value == 42
    assert dut.ALU_comp.value == 0

         # set new values
    dut.rs1v.value = 0b0010101010110100100101011
    dut.imm_ext.value = 0b0000101000110100100101011
    dut.ALU_src1_sel.value = 2
    dut.ALU_src2_sel.value = 1
    dut.ALU_ctrl.value = 2


    # inputs should register just after 1 clock cycle
    await RisingEdge(dut.inst_en)
    await Timer(5, 'ns')
    assert dut.ALU_result.value == 0b0000101000110100100101011
    assert dut.ALU_comp.value == 0

             # set new values
    dut.rs1v.value = 15
    dut.rs2v.value = 25
    dut.ALU_src1_sel.value = 2
    dut.ALU_src2_sel.value = 0
    dut.ALU_ctrl.value = 5


    # inputs should register just after 1 clock cycle
    await RisingEdge(dut.inst_en)
    await Timer(5, 'ns')
    assert dut.ALU_result.value == 1
    assert dut.ALU_comp.value == 0

  # set new values
    dut.rs1v.value = 0b0010101010110100100101011
    dut.rs2v.value = 4
    dut.ALU_src1_sel.value = 2
    dut.ALU_src2_sel.value = 0
    dut.ALU_ctrl.value = 2


    # inputs should register just after 1 clock cycle
    await RisingEdge(dut.inst_en)
    await Timer(5, 'ns')
    assert dut.ALU_result.value == 0b1010101101001001010110000
    assert dut.ALU_comp.value == 0

def test_alu():
    sim = os.getenv("SIM", "icarus")
    proj_path = Path(__file__).resolve().parent
    sources = list((proj_path.parent / "src").glob("ALU.sv"))
    print(sources)
    runner = get_runner(sim)
    runner.build(
        sources=sources,
        hdl_toplevel="ALU",
        always=True,
        timescale=("1ns", "1ps")
    )

    runner.test(hdl_toplevel="ALU", test_module="test_alu,",
        timescale=("1ns", "1ps"))

if __name__ == '__main__':
    test_alu()
