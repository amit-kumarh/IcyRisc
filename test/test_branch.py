# test_branch.py
import cocotb
import os
from pathlib import Path
import random
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge
from cocotb.types import Array
from cocotb_tools.runner import get_runner

from constants import OP_BTYPE

FUNCT3_BEQ = 0b000
FUNCT3_BNE = 0b001
FUNCT3_BLT = 0b100
FUNCT3_BGE = 0b101
FUNCT3_BLTU = 0b110
FUNCT3_BGEU = 0b111

RS1 = 1
RS2 = 2

def assemble_b_instruction(funct3, rs1, rs2, imm):
    """Assembles a B-type (branch) instruction."""
    b_imm12 = (imm >> 12) & 0x1
    b_imm10_5 = (imm >> 5) & 0x3F
    b_imm4_1 = (imm >> 1) & 0xF
    b_imm11 = (imm >> 11) & 0x1
    return (b_imm12 << 31) | (b_imm10_5 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (b_imm4_1 << 8) | (b_imm11 << 7) | (OP_BTYPE << 0)

async def initialize_registers(dut, reg_indexes, values):
    """Initializes a specific register in the register file."""
    current_registers = list(dut.reg0.register_file.value)
    for reg_index, value in zip(reg_indexes, values):
        current_registers[reg_index] = value
    dut.reg0.register_file.value = Array(current_registers)

async def run_branch_test(dut, inst, rs1_val, rs2_val, expected_pc):
    """Runs a single branch instruction test."""
    dut.SW.value = 0
    dut.inst.value = inst
    clock = Clock(dut.clk, 80, unit="ns")
    cocotb.start_soon(clock.start(start_high=False))

    # Reset registers here
    await RisingEdge(dut.clk)
    dut.SW.value = 1

    await RisingEdge(dut.clk)  # FETCH
    await RisingEdge(dut.clk)  # DECODE
    await FallingEdge(dut.clk)
    print(f"Branch Target Offset: 0x{int(dut.alu_result.value):08X}")
    await RisingEdge(dut.clk)  # BRANCH
    await FallingEdge(dut.clk)

    print(dut.alu0.src1_result.value)
    print(dut.imm_ext.value)
    print(dut.alu0.ALU_ctrl.value)
    print(dut.alu_result.value)

    print("rs1", hex(dut.alu0.src1_result.value))
    print("rs2", hex(dut.alu0.src2_result.value))
    print("alu_op", dut.alu0.ALU_ctrl.value)
    print("alu_cmp", dut.alu0.ALU_comp.value)
    print("Branch", dut.c0.b0.branch.value)
    print("f3", dut.c0.b0.funct3.value)
    print("alu_comp", dut.c0.b0.alu_comp.value)
    print("branch_ctrl", dut.c0.b0.branch_ctrl.value)

    await RisingEdge(dut.clk)  # FETCH

    await FallingEdge(dut.clk)
    actual_pc = int(dut.pc.value)
    print(f"PC after (potential) branch: 0x{actual_pc:08X}")

    assert actual_pc == expected_pc

@cocotb.test()
async def test_beq_taken(dut):
    """Tests BEQ when the branch is taken."""
    rs1_val = 0x1234
    rs2_val = 0x1234
    await initialize_registers(dut, [RS1, RS2], [rs1_val, rs2_val])
    imm = 0x00000010  # Branch forward 16 bytes
    inst = assemble_b_instruction(FUNCT3_BEQ, 1, 2, imm)
    print("INST", bin(inst))
    await run_branch_test(dut, inst, rs1_val, rs2_val, imm)

@cocotb.test()
async def test_beq_not_taken(dut):
    """Tests BEQ when the branch is not taken."""
    rs1_val = 0x1234
    rs2_val = 0x5678
    await initialize_registers(dut, [RS1, RS2], [rs1_val, rs2_val])
    imm = 0x00000010
    inst = assemble_b_instruction(FUNCT3_BEQ, 1, 2, imm)
    await run_branch_test(dut, inst, rs1_val, rs2_val, 4)

@cocotb.test()
async def test_bne_taken(dut):
    """Tests BNE when the branch is taken."""
    rs1_val = 0x1234
    rs2_val = 0x5678
    await initialize_registers(dut, [RS1, RS2], [rs1_val, rs2_val])
    imm = 0x00000010
    inst = assemble_b_instruction(FUNCT3_BNE, 1, 2, imm)
    await run_branch_test(dut, inst, rs1_val, rs2_val, imm)

@cocotb.test()
async def test_bne_not_taken(dut):
    """Tests BNE when the branch is not taken."""
    rs1_val = 0x1234
    rs2_val = 0x1234
    await initialize_registers(dut, [RS1, RS2], [rs1_val, rs2_val])
    imm = 0x00000010
    inst = assemble_b_instruction(FUNCT3_BNE, 1, 2, imm)
    await run_branch_test(dut, inst, rs1_val, rs2_val, 4)

@cocotb.test()
async def test_blt_taken(dut):
    """Tests BLT (signed <) when the branch is taken."""
    rs1_val = -5
    rs2_val = 10
    await initialize_registers(dut, [RS1, RS2], [rs1_val, rs2_val])
    imm = 0x00000010
    inst = assemble_b_instruction(FUNCT3_BLT, 1, 2, imm)
    await run_branch_test(dut, inst, rs1_val, rs2_val, imm)

@cocotb.test()
async def test_blt_not_taken(dut):
    """Tests BLT when the branch is not taken."""
    rs1_val = 15
    rs2_val = 10
    await initialize_registers(dut, [RS1, RS2], [rs1_val, rs2_val])
    imm = 0x00000010
    inst = assemble_b_instruction(FUNCT3_BLT, 1, 2, imm)
    await run_branch_test(dut, inst, rs1_val, rs2_val, 4)

@cocotb.test()
async def test_bge_taken(dut):
    """Tests BGE (signed >=) when the branch is taken."""
    rs1_val = 10
    rs2_val = 10
    await initialize_registers(dut, [RS1, RS2], [rs1_val, rs2_val])
    imm = 0x00000010
    inst = assemble_b_instruction(FUNCT3_BGE, 1, 2, imm)
    await run_branch_test(dut, inst, rs1_val, rs2_val, imm)

@cocotb.test()
async def test_bge_not_taken(dut):
    """Tests BGE when the branch is not taken."""
    rs1_val = 5
    rs2_val = 10
    await initialize_registers(dut, [RS1, RS2], [rs1_val, rs2_val])
    imm = 0x00000010
    inst = assemble_b_instruction(FUNCT3_BGE, 1, 2, imm)
    await run_branch_test(dut, inst, rs1_val, rs2_val, 4)

@cocotb.test()
async def test_bltu_taken(dut):
    """Tests BLTU (unsigned <) when the branch is taken."""
    rs1_val = 0x00000010  # Small unsigned
    rs2_val = 0xFFFFFFF0  # Large unsigned
    await initialize_registers(dut, [RS1, RS2], [rs1_val, rs2_val])
    imm = 0x00000010
    inst = assemble_b_instruction(FUNCT3_BLTU, 1, 2, imm)
    await run_branch_test(dut, inst, rs1_val, rs2_val, imm)

@cocotb.test()
async def test_bltu_not_taken(dut):
    """Tests BLTU when the branch is not taken."""
    rs1_val = 0x00000020
    rs2_val = 0x00000010
    await initialize_registers(dut, [RS1, RS2], [rs1_val, rs2_val])
    imm = 0x00000010
    inst = assemble_b_instruction(FUNCT3_BLTU, 1, 2, imm)
    await run_branch_test(dut, inst, rs1_val, rs2_val, 4)

@cocotb.test()
async def test_bgeu_taken(dut):
    """Tests BGEU (unsigned >=) when the branch is taken."""
    rs1_val = 0xFFFFFFF0 # large unsigned
    rs2_val = 0x00000010 # small unsigned
    await initialize_registers(dut, [RS1, RS2], [rs1_val, rs2_val])
    imm = 0x00000010
    inst = assemble_b_instruction(FUNCT3_BGEU, 1, 2, imm)
    await run_branch_test(dut, inst, rs1_val, rs2_val, imm)

@cocotb.test()
async def test_bgeu_not_taken(dut):
    """Tests BGEU when the branch is not taken."""
    rs1_val = 0x00000005
    rs2_val = 0x00000010
    await initialize_registers(dut, [RS1, RS2], [rs1_val, rs2_val])
    imm = 0x00000010
    inst = assemble_b_instruction(FUNCT3_BGEU, 1, 2, imm)
    await run_branch_test(dut, inst, rs1_val, rs2_val, 4)

def test_branch():
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
        test_module="test_branch",
        timescale=("10ns", "1ps"),
        hdl_toplevel_lang="verilog",
    )

if __name__ == "__main__":
    test_branch()
