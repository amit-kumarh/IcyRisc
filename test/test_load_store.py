# test_load_store.py
import cocotb
import os
from pathlib import Path
import random
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge
from cocotb.types import Array
from cocotb_tools.runner import get_runner

from constants import *
FUNCT3_WORD = 0b010
FUNCT3_HALF = 0b001
FUNCT3_HALF_UNSIGNED = 0b101
FUNCT3_BYTE = 0b000
FUNCT3_BYTE_UNSIGNED = 0b100

## THIS USES THE `test_mem` INITIAL FILE IN //programs
# this is a simple file with 4 words written to memory and the rest zeroed out
# 0x40 0x12345678
# 0x41 0x87654321
# 0x42 0xDEADBEEF
# 0x43 0xBEEFDEAD


def assemble_i_instruction(opcode, funct3, rd, rs1, imm):
    """Assembles an I-type instruction (used for loads)."""
    return (imm & 0xFFF) << 20 | (rs1 & 0x1F) << 15 | (funct3 & 0x7) << 12 | (rd & 0x1F) << 7 | (opcode & 0x7F)

def assemble_s_instruction(funct3, rs1, rs2, imm):
    """Assembles an S-type instruction (used for stores)."""
    imm12_5 = (imm >> 5) & 0x7F
    imm4_0 = imm & 0x1F
    return (imm12_5 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (imm4_0 << 7) | OP_STYPE

async def initialize_registers(dut, reg_indexes, values):
    """Initializes a specific register in the register file."""
    current_registers = list(dut.reg0.register_file.value)
    for reg_index, value in zip(reg_indexes, values):
        current_registers[reg_index] = value
    dut.reg0.register_file.value = Array(current_registers)

async def run_store_test(dut, inst):
    """Runs a single store instruction test."""
    dut.SW.value = 0
    dut.inst.value = 0
    clock = Clock(dut.clk, 80, unit="ns")
    cocotb.start_soon(clock.start(start_high=False))

    # Reset registers here
    await RisingEdge(dut.clk)
    dut.SW.value = 1

    await RisingEdge(dut.clk)  # FETCH
    dut.inst.value = inst
    await RisingEdge(dut.clk)  # DECODE
    await RisingEdge(dut.clk)  # MEM_ADDR (Address calculation)
    await FallingEdge(dut.clk)
    print(f"Store Address: 0x{int(dut.alu0.ALU_result.value):08X}")
    await RisingEdge(dut.clk)  # MEM_STORE
    await FallingEdge(dut.clk)
    print(f"Stored Data: 0x{int(dut.mem0.write_data.value):08X}")
    await RisingEdge(dut.clk)  # FETCH
    await FallingEdge(dut.clk)

    # run a load_test afterword to confirm the store worked

async def run_load_test(dut, inst, rd_index, expected_data):
    """Runs a single load instruction test."""
    dut.SW.value = 0
    dut.inst.value = 0
    clock = Clock(dut.clk, 80, unit="ns")
    cocotb.start_soon(clock.start(start_high=False))

    # Reset registers here
    await RisingEdge(dut.clk)
    dut.SW.value = 1

    await RisingEdge(dut.clk)  # FETCH
    dut.inst.value = inst
    await RisingEdge(dut.clk)  # DECODE
    await RisingEdge(dut.clk)  # MEM_ADDR
    await RisingEdge(dut.clk)  # MEM_LOAD
    await FallingEdge(dut.clk)
    print(f"Load Address: 0x{int(dut.mem0.read_address.value):08X}")
    await RisingEdge(dut.clk)  # MEM_WB
    await FallingEdge(dut.clk)
    print(f"Loaded Data: 0x{int(dut.mem0.read_data.value):08X}")
    await RisingEdge(dut.clk)  # FETCH

    await FallingEdge(dut.clk)  # wait a bit so the last cycle registers

    actual_data = dut.reg0.register_file.value[rd_index]
    print(f"Got 0x{int(actual_data):08X}, Expected 0x{expected_data:08X}")
    assert actual_data == expected_data


@cocotb.test()
async def test_lw(dut):
    """Tests the Load Word (LW) instruction."""
    rd = 10
    rs1 = 11
    base_address = 0x00000040
    offset = 0
    await initialize_registers(dut, [rs1], [base_address])
    imm = offset
    inst = assemble_i_instruction(OP_LOAD, FUNCT3_WORD, rd, rs1, imm)
    expected_data = 0x12345678  # Data at address 0x40

    await run_load_test(dut, inst, rd, expected_data)

@cocotb.test()
async def test_lw_half(dut):
    """Tests the Load Word (LW) instruction."""
    rd = 10
    rs1 = 11
    base_address = 0x00000042
    offset = 0
    await initialize_registers(dut, [rs1], [base_address])
    imm = offset
    inst = assemble_i_instruction(OP_LOAD, FUNCT3_HALF, rd, rs1, imm)
    expected_data = 0x1234 # Data at address 0x40

    await run_load_test(dut, inst, rd, expected_data)

@cocotb.test()
async def test_lw_byte(dut):
    """Tests the Load Word (LW) instruction."""
    rd = 10
    rs1 = 11
    base_address = 0x00000042
    offset = 0
    await initialize_registers(dut, [rs1], [base_address])
    imm = offset
    inst = assemble_i_instruction(OP_LOAD, FUNCT3_BYTE, rd, rs1, imm)
    expected_data = 0x34 # Data at address 0x40

    await run_load_test(dut, inst, rd, expected_data)

@cocotb.test()
async def test_lw_offset(dut):
    """Tests LW with a non-zero offset."""
    rd = 12
    rs1 = 13
    base_address = 0x00000040
    offset = 8
    await initialize_registers(dut, [rs1], [base_address])
    imm = offset
    inst = assemble_i_instruction(OP_LOAD, FUNCT3_WORD, rd, rs1, imm)
    expected_data = 0xDEADBEEF  # Data at address 0x44

    await run_load_test(dut, inst, rd, expected_data)

@cocotb.test()
async def test_sw(dut):
    """Tests the Store Word (SW) instruction."""
    rs1 = 14
    rs2 = 15
    base_address = 0x0000003C
    offset = 0
    store_data = 0xABCDEF01
    await initialize_registers(dut, [rs1, rs2], [base_address, store_data])
    imm = offset
    inst = assemble_s_instruction(FUNCT3_WORD, rs1, rs2, imm)
    await run_store_test(dut, inst)

    inst = assemble_i_instruction(OP_LOAD, FUNCT3_WORD, 16, rs1, imm)
    await run_load_test(dut, inst, 16, store_data)

@cocotb.test()
async def test_sw_half(dut):
    """Tests the Store Word (SW) instruction."""
    rs1 = 14
    rs2 = 15
    base_address = 0x00000050
    offset = 0
    store_data = 0xABCD
    await initialize_registers(dut, [rs1, rs2], [base_address, store_data])
    imm = offset
    inst = assemble_s_instruction(FUNCT3_HALF, rs1, rs2, imm)
    await run_store_test(dut, inst)

    inst = assemble_i_instruction(OP_LOAD, FUNCT3_HALF_UNSIGNED, 16, rs1, imm)
    await run_load_test(dut, inst, 16, store_data)

@cocotb.test()
async def test_sw_byte(dut):
    """Tests the Store Word (SW) instruction."""
    rs1 = 14
    rs2 = 15
    base_address = 0x00000050
    offset = 1
    store_data = 0xAB
    await initialize_registers(dut, [rs1, rs2], [base_address, store_data])
    imm = offset
    inst = assemble_s_instruction(FUNCT3_BYTE, rs1, rs2, imm)
    await run_store_test(dut, inst)

    inst = assemble_i_instruction(OP_LOAD, FUNCT3_BYTE_UNSIGNED, 16, rs1, imm)
    await run_load_test(dut, inst, 16, store_data)

@cocotb.test()
async def test_sw_offset(dut):
    """Tests SW with a non-zero offset."""
    rs1 = 17
    rs2 = 18
    base_address = 0x00000030
    offset = 4 # 0x34
    store_data = 0xFEDCBA98
    await initialize_registers(dut, [rs1, rs2], [base_address, store_data])
    imm = offset
    funct3 = 0b010  # FUNCT3 for SW
    inst = assemble_s_instruction(funct3, rs1, rs2, imm)
    await run_store_test(dut, inst)

    inst = assemble_i_instruction(OP_LOAD, FUNCT3_WORD, 19, rs1, imm)
    await run_load_test(dut, inst, 19, store_data)

def test_load_store():
    sim = os.getenv("SIM", "icarus")
    proj_path = Path(__file__).resolve().parent.parent
    os.environ["PROJ_ROOT"] = str(proj_path)
    sources = str(proj_path / "top.f")
    memory_init_file = str(proj_path / "programs" / "test_mem") # Assuming memory_init.mem is in the same directory

    runner = get_runner(sim)
    runner.build(
        hdl_toplevel="top",
        always=True,
        timescale=("10ns", "1ps"),
        build_args=["-c", sources],
        defines={"MEM_FILE_PATH_PREFIX": memory_init_file}
    )

    runner.test(
        hdl_toplevel="top",
        test_module="test_load_store",
        timescale=("10ns", "1ps"),
        hdl_toplevel_lang="verilog",
    )

if __name__ == "__main__":
    test_load_store()
