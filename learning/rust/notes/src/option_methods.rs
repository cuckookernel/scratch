
pub fn demo_option_methods() {

    let none_int = None;

    let val1 = Some(2).unwrap();
    println!("val1: {val1}");
    // none.unwrap();  this will panic!

    let or_1: Option<i32> = Some(1).or(Some(2));
    assert_eq!(or_1, Some(1));

    let or_2: Option<i32> = None.or(Some(2));
    assert_eq!(or_2, Some(2));
    println!("or_result2: {or_2:?}");

    let or_else_1: Option<i32> = Some(1).or_else(|| { Some(2) });
    assert_eq!(or_else_1, Some(1));

    let or_else_2: Option<i32> = none_int.or_else(|| { Some(2) });
    assert_eq!(or_else_2, Some(2));

    let unwrap_or_1: i32 = Some(1).unwrap_or(2);
    assert_eq!(unwrap_or_1, 1);

    let unwrap_or_2: i32 = None.unwrap_or(2);
    assert_eq!(unwrap_or_2, 2);

    let unwrap_or_else_1: i32 = Some(1).unwrap_or_else(|| {2});
    assert_eq!(unwrap_or_else_1, 1);

    let unwrap_or_else_2: i32 = None.unwrap_or_else(|| {2});
    assert_eq!(unwrap_or_else_2, 2);

    let unwrap_or_default_1: i32 = Some(1).unwrap_or_default();
    assert_eq!(unwrap_or_default_1, 0);

    let unwrap_or_default_2: i32 = None.unwrap_or_default();
    assert_eq!(unwrap_or_default_2, 0);

    let and_then_1: Option<i32> = Some(1).and_then(|val| {assert_eq!(val, 1); Some(2)} );
    assert_eq!(and_then_1, Some(2));

    if let Some(val) = Some(1) {
        assert_eq!(val, 1);
        println!("This branch runs!");
    } else {
        assert!(false);
        println!("This branch won't run");
    }

    let mut some1 = Some(1);
    let val1 = some1.take();
    assert_eq!(val1, Some(1));
    assert_eq!(some1, None);  // option is now empty!

    // .replace(T) = replace old value in place and return previous value of option.
    let prev_val: Option<i32> = some1.replace(2);
    assert_eq!(prev_val, None);
    assert_eq!(some1, Some(2));

    // .insert(T): insert a new value (and drop previous if any), return reference to new internal value.
    let curr_val_ref: &mut i32 = some1.insert(3);
    assert_eq!(*curr_val_ref, 3);

    // Note unwrap_or_default is only defined on Option<T>  if need T : Default
}