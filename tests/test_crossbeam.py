from test_harness import expect_summaries

def test_crossbeam_atomic_cell(tmpdir):
    src = """
        use crossbeam::atomic::AtomicCell;

        let atomic_cell = AtomicCell::new(42);
    """
    expect_summaries(tmpdir, src, {
        "atomic_cell": "42",
    })