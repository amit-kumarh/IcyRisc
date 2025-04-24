# test_jump.py
import cocotb
import os
from pathlib import Path
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge
from cocotb.types import Array
from cocotb_tools.runner import get_runner

from constants import OP_JAL, OP_JALR

def assemble_jal_instruction(rd, imm):
    """Assembles a JAL (Jump and Link) instruction."""
    j_imm20 = (imm >> 20) & 0x1
    j_imm10_1 = (imm >> 1) & 0x3FF
    j_imm11 = (imm >> 11) & 0x1
    j_imm19_12 = (imm >> 12) & 0xFF
    return (j_imm20 << 31) | (j_imm19_12 << 12) | (j_imm11 << 20) | (j_imm10_1 << 21) | (rd << 7) | (OP_JAL << 0)

def assemble_jalr_instruction(rd, rs1, imm):
    """Assembles a JALR (Jump and Link Register) instruction."""
    funct3 = 0b000
    return (imm & 0xFFF) << 20 | (rs1 & 0x1F) << 15 | (funct3 & 0x7) << 12 | (rd & 0x1F) << 7 | (OP_JALR & 0x7F)

async def initialize_register(dut, reg_index, value):
    """Initializes a specific register in the register file."""
    current_registers = list(dut.reg0.register_file.value)
    current_registers[reg_index] = value
    dut.reg0.register_file.value = Array(current_registers)

async def run_jump_test(dut, inst, rd_index, expected_rd_value, expected_pc_offset):
    """Runs a single jump instruction test."""
    dut.SW.value = 0
    dut.inst.value = inst
    clock = Clock(dut.clk, 80, unit="ns")
    cocotb.start_soon(clock.start(start_high=False))

    # reset registers here
    await RisingEdge(dut.clk)
    dut.SW.value = 1

    await RisingEdge(dut.clk)  # FETCH
    await RisingEdge(dut.clk)  # DECODE
    await RisingEdge(dut.clk)  # JUMP
    await RisingEdge(dut.clk)  # ALU_WB
    await RisingEdge(dut.clk)  # FETCH

    actual_pc_offset = int(dut.pc.value) - int(dut.pc_old.value)

    await FallingEdge(dut.clk)
    print(f"Jump Target Offset: 0x{int(dut.pc.value):08X}")
    print(f"PC after Jump: 0x{int(dut.pc.value):08X}")
    print(f"Value written to rd: 0x{int(dut.reg0.register_file.value[rd_index]):08X}")

    actual_rd_value = int(dut.reg0.register_file.value[rd_index])

    print(f"Got rd = 0x{actual_rd_value:08X}, Expected rd = 0x{expected_rd_value:08X}")
    print(f"Got PC Offset = 0x{actual_pc_offset:08X}, Expected PC Offset = 0x{expected_pc_offset:08X}")

    assert actual_rd_value == expected_rd_value
    assert actual_pc_offset == expected_pc_offset

@cocotb.test()
async def test_jal(dut):
    """Tests the JAL (Jump and Link) instruction."""
    rd = 1
    imm = 0x00000200  # Jump forward 512 bytes
    inst = assemble_jal_instruction(rd, imm)
    expected_rd_value = 4 # PC starts at 0, expect RA to be PC+4
    expected_pc_offset = imm
    await run_jump_test(dut, inst, rd, expected_rd_value & 0xFFFFFFFF, expected_pc_offset & 0xFFFFFFFF)

@cocotb.test()
async def test_jal_backward(dut):
    """Tests JAL with a backward jump."""
    rd = 2
    imm = -0x00000200 # Jump backward 512 bytes
    inst = assemble_jal_instruction(rd, imm)
    expected_rd_value = 4
    expected_pc_offset = imm
    await run_jump_test(dut, inst, rd, expected_rd_value & 0xFFFFFFFF, expected_pc_offset & 0xFFFFFFFF)

@cocotb.test()
async def test_jalr(dut):
    """Tests the JALR (Jump and Link Register) instruction."""
    rd = 3
    rs1 = 4
    imm = 0x00000020  # Offset from rs1
    rs1_val = 0x00000010
    await initialize_register(dut, rs1, rs1_val)
    inst = assemble_jalr_instruction(rd, rs1, imm)
    expected_rd_value = 4
    expected_pc_offset = (rs1_val + imm) & 0xFFFFFFFF
    await run_jump_test(dut, inst, rd, expected_rd_value & 0xFFFFFFFF, expected_pc_offset)
 
@cocotb.test()
async def test_jalr_zero_offset(dut):
    """Tests JALR with zero offset."""
    rd = 5
    rs1 = 6
    imm = 0
    rs1_val = 0x00000100
    await initialize_register(dut, rs1, rs1_val)
    inst = assemble_jalr_instruction(rd, rs1, imm)
    expected_rd_value = 4
    expected_pc_offset = rs1_val
    await run_jump_test(dut, inst, rd, expected_rd_value & 0xFFFFFFFF, expected_pc_offset)

def test_jump():
    sim = os.getenv("SIM", "icarus")
    proj_path = Path(__file__).resolve().parent.parent
    os.environ["PROJ_ROOT"] = str(proj_path)
    sources = str(proj_path / "top.f")

    runner = get_runner(sim)
    runner.build(
        hdl_toplevel="top",
        always=True,
        timescale=("10ns", "1ps"),
        build_args=["-f", sources],
    )

    runner.test(
        hdl_toplevel="top",
        test_module="test_jump",
        timescale=("10ns", "1ps"),
        hdl_toplevel_lang="verilog",
    )

if __name__ == '__main__':
    test_jump()
