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

    println!("</enums>");
}

fn collections() {
    let array = [1, 2, 3];
    let v = vec![1, 2, 3];
    let vd = VecDeque::from_iter([1, 2, 3]);
    println!("</collections>");
}

fn main() {
    enums();
    collections();
}
