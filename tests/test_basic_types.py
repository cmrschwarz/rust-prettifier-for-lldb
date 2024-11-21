from test_harness import expect_summaries


def test_u8(tmpdir):
    src = """
        let x: u8 = 65;
    """
    expect_summaries(tmpdir, src, {
        "x": "65",
    })


def test_char(tmpdir):
    src = """
        let x: char = 'A';
        let y: char = '\\n';
    """
    expect_summaries(tmpdir, src, {
        "x": "'A'",
        "y": "U+0x0000000A"
    })


def test_str(tmpdir):
    src = """
        let x: &str = "foo";
        let y: String = "bar".into();
    """
    expect_summaries(tmpdir, src, {
        "x": "\"foo\"",
        "y": "\"bar\""
    })
