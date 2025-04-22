import cocotb
import os
from pathlib import Path
import random
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge
from cocotb.types import Array
from cocotb_tools.runner import get_runner

## THIS USES THE `test_mem` INITIAL FILE IN //programs
# this is a simple file with 4 words written to memory and the rest zeroed out
# 0x40 0x12345678
# 0x41 0x87654321
# 0x42 0xDEADBEEF
# 0x43 0xBEEFDEAD

def test_all_inst():
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
        test_module=["test_itype", "test_rtype",  "test_utype", "test_branch", "test_jump", "test_load_store"],
        timescale=("10ns", "1ps"),
        hdl_toplevel_lang="verilog",
    )

if __name__ == "__main__":
    test_all_inst()
