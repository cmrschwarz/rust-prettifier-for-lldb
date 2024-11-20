from harness import run_rust_test


def test_u8(tmpdir):
    src = """
        let x: u8 = 65;
    """
    run_rust_test(tmpdir, src, {
        "x": "65",
    })


def test_char(tmpdir):
    src = """
        let x: char = 'A';
        let y: char = '\\n';
    """
    run_rust_test(tmpdir, src, {
        "x": "'A'",
        "y": "U+0x0000000A"
    })


def test_basic_vec_deque(tmpdir):
    src = """
        use std::collections::VecDeque;
        let x = VecDeque::from([1,2,3]);
    """
    run_rust_test(tmpdir, src, {
        "x": "(3) VecDeque[1, 2, 3]"
    })
