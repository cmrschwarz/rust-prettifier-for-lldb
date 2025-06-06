#![allow(clippy::all, unused)]

// Set a breakpoint where you want ot inspect and open your debug log.
// Use commands like `script lldb.frame.FindVariable("foo").GetNonSyntheticValue()`
// for interactive testing.

use std::{
    borrow::Cow,
    collections::{HashMap, VecDeque},
    rc::Rc,
    sync::Arc,
};

use core::iter::FromIterator;

fn basic_datatypes() {
    let x: char = 'A';
    let y: i8 = 65;
    let z: i8 = -128;
    let w: u8 = 65;

    let xx: i16 = 1000;
    let xy: u16 = 1000;

    println!("</basic_datatypes>")
}

#[derive(Default)]
struct StructWithManyMembers {
    x: i32,
    y: f64,
    z: i32,
    w: i32,
    q: i32,
    f: i32,
    g: i32,
}

enum A {
    X,
    Y,
    Z,
    V(Vec<i32>),
    D(StructWithManyMembers),
}

#[derive(Clone, PartialEq, Debug)]
pub enum B {
    Foo(Box<B>),
    Bar(Box<[B; 2]>),
    Baz(i32),
}

pub enum LargeEarly {
    Foo(Vec<i32>),

    Bar,
    Baz,
    Quux,
}

pub enum LargeMiddle {
    Foo,
    Bar,
    Baz(Vec<i32>),
    Quux,
}

pub enum LargeLate {
    Foo,
    Bar,
    Baz,
    Quux(Vec<i32>),
}

#[derive(Clone, PartialEq, Debug)]
pub enum TokenKind<'a> {
    Literal(Vec<u8>),
    Identifier(&'a str),

    Let,
    If,
    Else,
    True,
    False,
}

fn enums() {
    let vd = VecDeque::from([1, 2, 3]);
    let foo = StructWithManyMembers {
        x: 1,
        y: 3.2,
        ..Default::default()
    };
    let a = A::D(foo);

    let vec_in_enum = A::V(vec![1, 2, 3]);

    let long_vec_in_enum = A::V(Vec::from_iter(0..100));

    let b = B::Foo(Box::new(B::Baz(42)));

    let le1 = LargeEarly::Foo(vec![1]);
    let le2 = LargeEarly::Bar;
    let le3 = LargeEarly::Baz;
    let le4 = LargeEarly::Quux;

    let lm1 = LargeMiddle::Foo;
    let lm2 = LargeMiddle::Bar;
    let lm3 = LargeMiddle::Baz(vec![42]);
    let lm4 = LargeMiddle::Quux;

    let ll2 = LargeLate::Foo;
    let ll3 = LargeLate::Bar;
    let ll4 = LargeLate::Baz;
    let ll1 = LargeLate::Quux(vec![42]);

    let x = TokenKind::False;

    println!("</enums>");
}

// TODO: implement dependencies for our test harness
// and replace the hasmap access tests aswell as this.
// We need some way to get deterministic ordering though.
fn hashmap() {
    use std::collections::HashMap;
    use std::hash::{BuildHasherDefault, Hasher};
    use std::iter::FromIterator;
    #[derive(Default)]
    struct IdentityHash(u64);
    impl Hasher for IdentityHash {
        fn write(&mut self, _: &[u8]) {
            unimplemented!()
        }
        fn write_u8(&mut self, n: u8) {
            self.0 = u64::from(n)
        }
        fn write_u16(&mut self, n: u16) {
            self.0 = u64::from(n)
        }
        fn write_u32(&mut self, n: u32) {
            self.0 = u64::from(n)
        }
        fn write_u64(&mut self, n: u64) {
            self.0 = n
        }
        fn write_usize(&mut self, n: usize) {
            self.0 = n as u64
        }
        fn write_i8(&mut self, n: i8) {
            self.0 = n as u64
        }
        fn write_i16(&mut self, n: i16) {
            self.0 = n as u64
        }
        fn write_i32(&mut self, n: i32) {
            self.0 = n as u64
        }
        fn write_i64(&mut self, n: i64) {
            self.0 = n as u64
        }
        fn write_isize(&mut self, n: isize) {
            self.0 = n as u64
        }
        fn finish(&self) -> u64 {
            self.0
        }
    }
    let mut hm = HashMap::<i32, &'static str, BuildHasherDefault<IdentityHash>>::from_iter([
        (3, "foo"),
        (12, "bar"),
    ]);
    println!("</hashmap>");
}

fn collections() {
    let array = [1, 2, 3];
    let array_2 = [[1, 2, 3], [4, 5, 6]];
    let v = vec![1, 2, 3];
    let vd = VecDeque::from_iter([1, 2, 3]);

    let vec_i8 = vec![3i8, -1i8, 'A' as i8];

    let vec_char = vec!['A', 'B', 'C'];

    println!("</collections>");
}

fn std_lib_types() {
    let x = Box::new(42);

    let y = Box::new(Rc::new(42));

    let cow_str = Cow::<str>::Borrowed("asdf");

    let rc_string: Rc<String> = Rc::from("asdf".to_string());

    let rc_str: Rc<str> = Rc::from("asdf");

    let rc_slice = Rc::<[i32]>::from([1, 2, 3]);

    println!("</std_lib_types>");
}

// see https://github.com/cmrschwarz/rust-prettifier-for-lldb/issues/5
fn rc_of_vec() {
    const ARRAY: [i32; 3] = [1, 2, 3];

    let vec = Vec::from(ARRAY);

    let vec_deque = VecDeque::from(ARRAY);

    let rc_vec = Rc::new(Vec::from(ARRAY));

    let rc_vec_deque = Rc::new(VecDeque::from(ARRAY));

    let rc_slice: Rc<[i32]> = Rc::new(ARRAY);

    let rc_ref_slice: Rc<&[i32]> = Rc::new(&ARRAY);

    let arc_vec = Arc::new(Vec::from(ARRAY));

    let arc_vec_deque = Arc::new(VecDeque::from(ARRAY));

    let arc_slice: Arc<[i32]> = Arc::new(ARRAY);

    let arc_ref_slice: Arc<&[i32]> = Arc::new(&ARRAY[..]);

    println!("</rc_of_vec>");
}

enum MyEnum {
    A(&'static str),
    B(i32),
    C(Vec<i32>),
}

fn demo() {
    enum MyEnum {
        A,
        C { x: i32, y: f32 },
        D(Vec<i32>),
    }
    let a = MyEnum::A;
    let c = MyEnum::C { x: 1, y: 2.5 };
    let d = MyEnum::D(vec![1, 2, 3]);

    let cd = VecDeque::from_iter([1, 2, 3, 5, 423]);

    println!("</demo>");
}

fn main() {
    basic_datatypes();
    enums();
    hashmap();
    collections();
    std_lib_types();
    rc_of_vec();
    demo();
}
