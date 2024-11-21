#![allow(unused)]
// Set a breakpoint where you want ot inspect and open your debug log.
// Use commands like `script lldb.frame.FindVariable("foo").GetNonSyntheticValue()`
// for interactive testing.

use std::collections::VecDeque;

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
    //let vd = VecDeque::from([1, 2, 3]);
    //let foo = StructWithManyMembers {
    //    x: 1,
    //    y: 3.2,
    //    ..Default::default()
    //};
    //let a = A::D(foo);
    //
    //let vec_in_enum = A::V(vec![1, 2, 3]);
    //
    //let long_vec_in_enum = A::V(Vec::from_iter(0..100));
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

    println!("</enums>");
}

fn collections() {
    let array = [1, 2, 3];
    let v = vec![1, 2, 3];
    let vd = VecDeque::from_iter([1, 2, 3]);
    println!("</collections>");
}

enum MyEnum {
    A(&'static str),
    B(i32),
    C(Vec<i32>),
}

fn demo() {
    let myvec = vec![1, 2, 3];
    let mydeque = VecDeque::from_iter([4, 5, 6]);
    let myenum = MyEnum::B(42);
    let mystr = String::from("asdf");
    println!("</demo>");
}

fn main() {
    enums();
    collections();
    demo();
}
