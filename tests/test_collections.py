from harness import run_rust_test


def test_basic_vec(tmpdir):
    src = """
        let x = vec![1,2,3];
    """
    run_rust_test(tmpdir, src, {
        "x": "(3) vec![1, 2, 3]"
    })


def test_basic_vec_deque(tmpdir):
    src = """
        use std::collections::VecDeque;
        let x = VecDeque::from([1,2,3]);
    """
    run_rust_test(tmpdir, src, {
        "x": "(3) VecDeque[1, 2, 3]"
    })
