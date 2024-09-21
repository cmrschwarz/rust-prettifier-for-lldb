import pytest
import py
import os
import subprocess
import lldb
import sys
import textwrap

PRETTIFIER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "LLDB .py")

def run_rust_test(
    temp_dir: py.path.local,
    rust_src: str,
    expected_var_summaries: dict[str, str]
):
    src_path = os.path.join(str(temp_dir), "main.rs")
    rust_src = textwrap.indent(textwrap.dedent(rust_src), "    ")

    rust_src += "    let _ = 0 + 0;" # dummy line to place the breakpoint on

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
        assert result.stderr.decode("utf-8") == ""
        assert result.returncode == 0

    debugger: lldb.SBDebugger = lldb.SBDebugger.Create()
    debugger.SetAsync(False)

    target: lldb.SBTarget = debugger.CreateTargetWithFileAndArch(binary_path, lldb.LLDB_ARCH_DEFAULT)
    assert target


    breakpoint_line = len(rust_src.splitlines()) - 1
    breakpoint: lldb.SBBreakpoint= target.BreakpointCreateByLocation("main.rs", breakpoint_line)
    assert breakpoint.num_locations == 1

    process = target.LaunchSimple(None, None, ".")
    thread = process.GetThreadAtIndex(0)
    frame = thread.GetFrameAtIndex(0)
    assert frame

    repl: lldb.SBCommandInterpreter = debugger.GetCommandInterpreter()
    res = lldb.SBCommandReturnObject()
    repl.HandleCommand(f"command script import {PRETTIFIER_PATH}", res)
    assert res.Succeeded()

    for (name, summary) in expected_var_summaries.items():
        var = frame.FindVariable(name)
        s = var.GetSummary()
        if s is None:
            s = var.GetValue()
        assert s == summary

def test_basic_int(tmpdir):
    src = """
        let x = 3;
    """
    run_rust_test(tmpdir, src, {
        "x": "3"
    })


def test_c_style_enum(tmpdir):
    src = """
        enum CStyleEnum {
            A, B
        }
        let x = CStyleEnum::A;
    """
    run_rust_test(tmpdir, src, {
        "x": "A"  # TODO: change this to be Foo::A
    })


def test_basic_rust_enum(tmpdir):
    src = """
        enum Foo {
            A(u8), B(u16)
        }
        let x = Foo::A(42);
    """
    run_rust_test(tmpdir, src, {
        "x": "Foo::A(..)"
    })


def test_multi_enum_variant(tmpdir):
    src = """
        enum RegularEnum {
            A,
            B(i32, i32),
            C { x: i64, y: f64 },
        }
        let a = RegularEnum::A;
        let b = RegularEnum::B(1, 2);
        let c = RegularEnum::C{x: 1, y: 2.0};
    """
    run_rust_test(tmpdir, src, {
        "a": "RegularEnum::A"
    })


