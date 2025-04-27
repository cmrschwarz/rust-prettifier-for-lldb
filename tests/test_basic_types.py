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

        let rc_vec = Rc::new(Vec::from([1, 2, 3]));

        let rc_int = Rc::new(42);
        let rc_int_2 = rc_int.clone();

        let rc_string: Rc<String> = Rc::from("asdf".to_string());

        let rc_u8: Rc<u8> = Rc::from(42);
        let rc_str: Rc<str> = Rc::from("asdf");

        let rc_slice = Rc::<[i32]>::from([1, 2, 3]);


    """
    expect_summaries(tmpdir, src, {
        "rc_vec": "(strong:1) (3) vec![1, 2, 3]",
        "rc_slice": "(strong:1) [1, 2, 3]",
        "rc_str": "(strong:1) \"asdf\"",
        "rc_int": "(strong:2) 42",
        "rc_string": "(strong:1) \"asdf\"",
        "rc_u8": "(strong:1) 42",
    })

    expect_command_output(tmpdir, src, {
        ("v rc_vec[0]", "(int) rc_vec[0] = 1\n")
    })

def test_arc(tmpdir):
    src = """
        use std::sync::Arc;

        let arc_vec = Arc::new(Vec::from([1, 2, 3]));

        let arc_int = Arc::new(42);
        let arc_int_2 = arc_int.clone();

        let arc_string: Arc<String> = Arc::from("asdf".to_string());

        let arc_u8: Arc<u8> = Arc::from(42);
        let arc_str: Arc<str> = Arc::from("asdf");

        let weak = Arc::downgrade(&arc_str);

        let arc_slice = Arc::<[i32]>::from([1, 2, 3]);
    """
    expect_summaries(tmpdir, src, {
        "arc_vec": "(strong:1) (3) vec![1, 2, 3]",
        "arc_str": "(strong:1, weak:1) \"asdf\"",
        "arc_int": "(strong:2) 42",
        "arc_string": "(strong:1) \"asdf\"",
        "arc_u8": "(strong:1) 42",
        "arc_slice": "(strong:1) [1, 2, 3]",
    })

    expect_command_output(tmpdir, src, {
        ("v arc_vec[0]", "(int) arc_vec[0] = 1\n")
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

def test_cell(tmpdir):
    src = """
        use std::cell::{Cell, UnsafeCell};
        let safe = Cell::<i32>::new(42);
        let not_safe = UnsafeCell::<i32>::new(42);
    """

    expect_summaries(tmpdir, src, {
        "safe": "42",
        "not_safe": "42",
    })
