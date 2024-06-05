#[derive(Debug)]
struct S {
    a: i32,
    b: i32
}

use std::any::type_name;

use r#typeof::type_of;

fn main() {

    let x = 5;
    let x_ref = &x;

    let x = 6;

    println!("x={} x_ref={}", x, x_ref);

    const S1: S = S{a:1 , b:2};
    println!("S={S1:?}");

    S1.a = 3;
    println!("S={S1:?}");

    let s2 = &mut S{a: 1, b: 2};
    s2.a = 3;

    println!("S={s2:?} {b}", b=s2.b);

    // std::any::type_name::<typeof(32)>();
    let a = type_name::<S>();
    let t = type_of(s2);

}