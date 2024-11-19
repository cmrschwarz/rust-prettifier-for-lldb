from test_harness import run_rust_test


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


def test_option(tmpdir):
    src = """
        let opt_str1: Option<&str> = Some("string");
        let opt_str2: Option<&str> = None;
        let opt_str3: Option<*const u8> = Some("other string".as_ptr());
    """
    run_rust_test(tmpdir, src, {
        "opt_str1": "Some(\"string\")"
    })


def test_result(tmpdir):
    src = """
        let result_ok: Result<&str, String> = Ok("ok");
        let result_err: Result<&str, String> = Err("err".into());
    """
    run_rust_test(tmpdir, src, {
        "result_ok": "Ok(\"ok\")",
        "result_err": "Err(\"err\")"
    })


def test_cow(tmpdir):
    src = """
        use std::borrow::Cow;
        let cow1 = Cow::Borrowed("their cow");
        let cow2 = Cow::<str>::Owned("my cow".into());
    """
    run_rust_test(tmpdir, src, {
        "cow1": "Cow::Borrowed(\"their cow\")",
        "cow2": "Cow::Owned(\"my cow\")"
    })


def _broken_test_lld_crash(tmpdir):  # TODO: send a bugreport to LLD
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
    run_rust_test(tmpdir, src, {
        "baz": "Baz::Bar(Bar{x: 3})"
    })
