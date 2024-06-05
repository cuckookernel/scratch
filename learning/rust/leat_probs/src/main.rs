mod leet {
    pub mod two_sum;
    pub mod longest_palindromic;

}

use leet::two_sum;
use leet::longest_palindromic;


fn main() {
    let test = "balanced_ps";

    if test == "two_sum" {

        let _l1 = two_sum::ListNode::new(1);
        let _l2 = _l1.clone();
        two_sum::add_two_numbers(Some(Box::new(_l1)), Some(Box::new(_l2)));

    } else if test == "scratch" {
        scratch()
    } else if test == "l_pal" {
        let s = "tattarrattat".to_string();
        // let arr = s.as_bytes();
        let lpal = longest_palindromic::longest_palindrome(s);
        dbg!(lpal);
    }

    return
    // dbg!(v);
}

fn scratch() {
    let v: Vec<i32> = vec![1, 2, 3];
    let mut b1 = Box::new(v);
    let b2 = b1.clone();

    b1[2] =0;
    dbg!(b1);
    dbg!(b2);
}
