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


def test_hashmap_access(tmpdir):
    src = """
        use std::collections::HashMap;
        use std::hash::{Hasher, BuildHasherDefault};
        use std::iter::FromIterator;
        #[derive(Default)]
        struct IdentityHash(u64);
        impl Hasher for IdentityHash {
                fn write(&mut self, _: &[u8]) {unimplemented!()}
                fn write_u8(&mut self, n: u8)       { self.0 = u64::from(n) }
                fn write_u16(&mut self, n: u16)     { self.0 = u64::from(n) }
                fn write_u32(&mut self, n: u32)     { self.0 = u64::from(n) }
                fn write_u64(&mut self, n: u64)     { self.0 = n }
                fn write_usize(&mut self, n: usize) { self.0 = n as u64 }
                fn write_i8(&mut self, n: i8)       { self.0 = n as u64 }
                fn write_i16(&mut self, n: i16)     { self.0 = n as u64 }
                fn write_i32(&mut self, n: i32)     { self.0 = n as u64 }
                fn write_i64(&mut self, n: i64)     { self.0 = n as u64 }
                fn write_isize(&mut self, n: isize) { self.0 = n as u64 }
                fn finish(&self) -> u64 { self.0 }
        }
        let mut hm = HashMap::<i32, &'static str, BuildHasherDefault<IdentityHash>>::from_iter([
            (3, "foo"),
            (12, "bar"),
        ]);
   """
    # TODO: seems a bit sketchy. Can we improve this?
    expect_command_output(tmpdir, src, [
        ("v hm[0].0", "(int) 0 = 12\n")
    ])
