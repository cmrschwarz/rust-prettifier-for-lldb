#![allow(unused)]

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

fn main() {
    let v = vec![1, 2, 3];
    let vd = VecDeque::from([1, 2, 3]);
    let foo = StructWithManyMembers {
        x: 1,
        y: 3.2,
        ..Default::default()
    };
    let a = A::D(foo);
    println!("foo");
}
