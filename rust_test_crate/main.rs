#![allow(unused)]
// Set a breakpoint where you want ot inspect and open your debug log.
// Use commands like `script lldb.frame.FindVariable("foo").GetNonSyntheticValue()`
// for interactive testing.

use std::{
    collections::{HashMap, VecDeque},
    rc::Rc,
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

    println!("</std_lib_types>");
}

enum MyEnum {
    A(&'static str),
    B(i32),
    C(Vec<i32>),
}

fn demo() {
    enum MyEnum {
        A,
        B(&'static str),
        C { x: i32, y: f32 },
        D(Vec<i32>),
    }
    let a = MyEnum::A;
    let b = MyEnum::B("foo");
    let c = MyEnum::C { x: 1, y: 2.5 };
    let d = MyEnum::D(vec![1, 2, 3]);
    println!("</demo>");
}

fn main() {
    basic_datatypes();
    enums();
    hashmap();
    collections();
    std_lib_types();
    demo();
}
