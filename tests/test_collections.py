from test_harness import expect_summaries, expect_command_output


def test_basic_vec_summary(tmpdir):
    src = """
        let x = vec![1,2,3];
    """
    expect_summaries(tmpdir, src, {
        "x": "(3) vec![1, 2, 3]"
    })


def test_basic_vec_child_access(tmpdir):
    src = """
        let x = vec![1,2,3];
    """
    expect_command_output(tmpdir, src, [
        ("v x[1]", "(int) x[1] = 2\n")
    ])


def test_basic_vec_deque(tmpdir):
    src = """
        use std::collections::VecDeque;
        let x = VecDeque::from([1,2,3]);
    """
    expect_summaries(tmpdir, src, {
        "x": "(3) VecDeque[1, 2, 3]"
    })

# TODO: this is non deterministic. Find better way to test this.
# def test_hashmap_access(tmpdir):
#    src = """
#        use std::collections::HashMap;
#        use std::iter::FromIterator;
#        let hm = HashMap::<&'static str, i32>::from_iter([("foo", 3), ("bar", 12)]);
#    """
#    # TODO: seems a bit sketchy. Can we improve this?
#    expect_command_output(tmpdir, src, [
#        ("v hm[0].1", "(int) 1 = 3\n")
#    ])
