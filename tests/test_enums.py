from test_harness import expect_command_output, expect_summaries, run_rust_test


def test_basic_int(tmpdir):
    src = """
        let x = 3;
    """
    expect_summaries(tmpdir, src, {
        "x": "3"
    })


def test_c_style_enum(tmpdir):
    src = """
        enum CStyleEnum {
            A, B
        }
        let x = CStyleEnum::A;
    """
    expect_summaries(tmpdir, src, {
        "x": "A"  # TODO: change this to be Foo::A?
    })


def test_basic_rust_enum(tmpdir):
    src = """
        enum Foo {
            A(u8), B(u16)
        }
        let x = Foo::A(42);
    """
    expect_summaries(tmpdir, src, {
        "x": "Foo::A(42)"
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
        let c = RegularEnum::C{x: 1, y: 2.5};
    """
    expect_summaries(tmpdir, src, {
        "a": "RegularEnum::A",
        "b": "RegularEnum::B(1, 2)",
        "c": "RegularEnum::C{x: 1, y: 2.5}"
    })

def test_enum_with_niche_in_early_variant(tmpdir):
    src = """
        pub enum E {
            Foo(Vec<i32>),
            Bar,
            Baz,
            Quux,
        }
        let foo = E::Foo(vec![1, 2]);
        let bar = E::Bar;
        let baz = E::Baz;
        let quux = E::Quux;
    """
    expect_summaries(tmpdir, src, {
        # TODO: the discriminator for this case ends up just being the
        # the length of the vector. We have no way of doing the correct
        # thing here.
        # "foo": "E::Foo((2) vec![1, 2])",
        "bar": "E::Bar",
        "baz": "E::Baz",
        "quux": "E::Quux",
    })



def test_enum_with_niche_in_middle_variant(tmpdir):
    src = """
        pub enum E {
            Foo,
            Bar,
            Baz(Vec<i32>),
            Quux,
        }
        let foo = E::Foo;
        let bar = E::Bar;
        let baz = E::Baz(vec![1]);
        let quux = E::Quux;
    """
    expect_summaries(tmpdir, src, {
        "foo": "E::Foo",
        "bar": "E::Bar",
        # TODO: see `test_enum_with_niche_in_early_variant`. We are screwed here.
        #"baz": "E::Baz((3) vec![1, 2, 3])",
        "quux": "E::Quux",
    })

def test_enum_with_niche_in_late_variant(tmpdir):
    src = """
        pub enum E {
            Foo,
            Bar,
            Baz,
            Quux(Vec<i32>),
        }
        let foo = E::Foo;
        let bar = E::Bar;
        let baz = E::Baz;
        let quux = E::Quux(vec![1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]);
    """
    expect_summaries(tmpdir, src, {
        "foo": "E::Foo",
        "bar": "E::Bar",
        "baz": "E::Baz",
        "quux": "E::Quux((15) vec![1, 2, 3, 4, 5, 6, 7, 8, 9, 10, ...])",
    })



def test_option(tmpdir):
    src = """
        let opt_str1: Option<&str> = Some("foobar");
        let opt_str2: Option<&str> = None;
        let opt_str3: Option<*const u8> = Some("other string".as_ptr());
    """
    expect_summaries(tmpdir, src, {
        "opt_str1": "Some(\"foobar\")"
    })


def test_result(tmpdir):
    src = """
        let result_ok: Result<&str, String> = Ok("ok");
        let result_err: Result<&str, String> = Err("err".into());
    """
    expect_summaries(tmpdir, src, {
        "result_ok": "Ok(\"ok\")",
        "result_err": "Err(\"err\")"
    })


def test_cow(tmpdir):
    src = """
        use std::borrow::Cow;
        let cow1 = Cow::Borrowed("their cow");
        let cow2 = Cow::<str>::Owned("my cow".into());
    """
    expect_summaries(tmpdir, src, {
        "cow1": "Borrowed(\"their cow\")",
        "cow2": "Owned(\"my cow\")",
    })


def test_pointer_niche(tmpdir):
    src = """
        enum MyEnum {
            A(&'static str),
            B(i32),
            C(Vec<i32>),
        }
        let myenum = MyEnum::B(42);
    """
    expect_summaries(tmpdir, src, {
        "myenum": "MyEnum::B(42)",
    })


def test_struct_enum_synthetic(tmpdir):
    src = """
        enum Foo{
            Bar(Baz)
        }
        struct Baz{x: i32, y: i32}

        let foo = Foo::Bar(Baz{x: 1, y: 2});
    """

    def compare_synth(_dbg, frame):
        foo = frame.FindVariable("foo")
        foo_s = foo.GetSummary()
        assert foo_s == 'Foo::Bar(Bar{x: 1, y: 2})'
        x = foo.GetChildAtIndex(0)
        x_s = x.GetValue()
        assert x_s == "1"

    run_rust_test(tmpdir, src, compare_synth)


def test_access_vec_in_enum(tmpdir):
    src = """
        enum Foo{
            A(Vec<i32>),
            B(Vec<i64>)
        }
        let x = Foo::A(vec![1, 2, 3]);
    """
    expect_command_output(tmpdir, src, [
        ("settings set target.enable-synthetic-value true", ""),
        ("v x[1]", "(int) x[1] = 2\n")
    ])


def _broken_test_lld_crash(tmpdir):  # TODfooO: send a bugreport to LLDB
    src = """
        use std::num::NonZeroI64;
        #[repr(C)]
        struct Foo {
            x: i64,
            y: NonZeroI64,
        }
        struct Bar {
            x: i64,
        }
        enum Baz {
            Foo(Foo),
            Bar(Bar),
        }
        let baz = Baz::Bar(Bar{x: 3});
    """
    expect_summaries(tmpdir, src, {
        "baz": "Baz::Bar(Bar{x: 3})"
    })
