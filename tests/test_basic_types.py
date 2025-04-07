from test_harness import expect_command_output, expect_summaries


def test_u8(tmpdir):
    src = """
        let x: u8 = 65;
    """
    expect_summaries(tmpdir, src, {
        "x": "65",
    })


# regression test for #2
def test_i8(tmpdir):
    src = """
        let x: i8 = -128;
    """

    # TODO: we would prefer to get rid of the
    # '\x80' here, but I have no idea how.
    # Disabling the cplusplus Category and other potentially conflicting
    # Sources did unfortunately not help.
    expect_command_output(tmpdir, src, [
        ("v x", "(char) x = '\\x80' -128\n")
    ])
    expect_summaries(tmpdir, src, {
        "x": "-128",
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
    expect_command_output(tmpdir, src, {
        ("v x", "(char32_t) x = U+0x00000041 'A'\n")
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



def test_rc(tmpdir):
    src = """
        use std::rc::Rc;

        let rc_int = Rc::new(42);
        let rc_int_2 = rc_int.clone();

        let rc_string: Rc<String> = Rc::from("asdf".to_string());

        let rc_u8: Rc<u8> = Rc::from(42);
        let rc_str: Rc<str> = Rc::from("asdf");
    """
    expect_summaries(tmpdir, src, {
        "rc_str": "(refs:1) \"asdf\"",
        "rc_int": "(refs:2) 42",
        "rc_string": "(refs:1) \"asdf\"",
        "rc_u8": "(refs:1) 42",
    })


def test_box(tmpdir):
    src = """
        let x = Box::new(42);
    """
    # TODO: currently raw summary text is just the pointer hex value,
    # consider showing Box(T) ?
    expect_command_output(tmpdir, src, [
        ("v *x", "(int) *x = 42\n"),
    ])


def test_tuple(tmpdir):
    src = """
        let x = (42, "foo");
    """
    # TODO: currently raw summary text is just the pointer hex value,
    # consider showing Box(T) ?
    expect_summaries(tmpdir, src, {
        "x": "(42, \"foo\")",
    })


def test_tuple_access(tmpdir):
    src = """
        let x = (42, "foo");
    """
    # '(int) 1'. meh.
    expect_command_output(tmpdir, src, [
        ("v x[0]", "(int) 0 = 42\n"),
        ("v x.0", "(int) 0 = 42\n"),
    ])
