import os
import subprocess
import lldb  # type: ignore
import textwrap
from typing import Any, Callable

PACKAGE_ROOT_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        ".."
    )
)
PRETTIFIER_PATH = os.path.join(
    PACKAGE_ROOT_PATH,
    "rust_prettifier_for_lldb.py"
)


def run_rust_test(
    temp_dir: Any,
    rust_src: str,
    test_code: Callable[[Any], None]
):
    src_path = os.path.join(str(temp_dir), "main.rs")
    rust_src = textwrap.indent(textwrap.dedent(rust_src), "    ")

    rust_src += "    let _ = 0 + 0;"  # dummy line to place the breakpoint on

    rust_src = "fn main() {\n" + rust_src + "\n}\n"

    binary_path = os.path.join(str(temp_dir), "main")
    with open(src_path, "w") as f:
        f.write(rust_src)

    result = subprocess.run(
        ["rustc", "-g", src_path, "-o", binary_path],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE
    )

    if result.returncode != 0:
        stderr = result.stderr.decode("utf-8")
        assert stderr == ""
        assert result.returncode == 0

    debugger: lldb.SBDebugger = lldb.SBDebugger.Create()
    debugger.SetAsync(False)

    target: lldb.SBTarget = debugger.CreateTargetWithFileAndArch(
        binary_path, lldb.LLDB_ARCH_DEFAULT)
    assert target

    breakpoint_line = len(rust_src.splitlines()) - 1
    breakpoint: lldb.SBBreakpoint = target.BreakpointCreateByLocation(
        "main.rs", breakpoint_line)
    assert breakpoint.num_locations == 1

    process = target.LaunchSimple(None, None, ".")
    thread = process.GetThreadAtIndex(0)
    frame = thread.GetFrameAtIndex(0)
    assert frame

    repl: lldb.SBCommandInterpreter = debugger.GetCommandInterpreter()
    res = lldb.SBCommandReturnObject()
    repl.HandleCommand(f"command script import {PRETTIFIER_PATH}", res)
    assert res.Succeeded()

    test_code(frame)

    lldb.SBDebugger.Destroy(debugger)


def compare_summaries(frame, expected_var_summaries):
    for (name, expected_summary) in expected_var_summaries.items():
        var = frame.FindVariable(name)
        s = var.GetSummary()
        if s is None:
            s = var.GetValue()
        assert s == expected_summary


def expect_summaries(
    temp_dir: Any,
    rust_src: str,
    expected_var_summaries: dict[str, str]
):
    run_rust_test(
        temp_dir,
        rust_src,
        lambda frame: compare_summaries(frame, expected_var_summaries)
    )
