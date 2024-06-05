// Definition for singly-linked list.

#[derive(PartialEq, Eq, Clone, Debug)]
pub struct ListNode {
  pub val: i32,
  pub next: Option<Box<ListNode>>
}

impl ListNode {
  #[inline]
  pub fn new(val: i32) -> Self {
    ListNode {
      next: None,
      val
    }
  }
}

pub fn reverse(l1: Option<Box<ListNode>>) -> Option<Box<ListNode>> {
  let mut rest = l1;
  let mut result: Option<Box<ListNode>> = None;

  while let Some(l) = rest {
    result = Some(Box::new(ListNode{ val: l.val, next: result}));
    rest = l.next;
  }

  return result
}

//struct Solution {}

// impl Solution {

  pub fn add_two_numbers(
    l1: Option<Box<ListNode>>,
    l2: Option<Box<ListNode>>
  ) -> Option<Box<ListNode>> {
    let mut l1_ = l1;
    let mut l2_ = l2;
    let mut carry : i32 = 0;

    let mut result: Option<Box<ListNode>> = None;

    while l1_.is_some() || l2_.is_some() || carry > 0 {
      let (v1, next_l1) =
        if let Some(l) = l1_ { (l.val, l.next) } else { (0, None)};
      let (v2, next_l2) =
        if let Some(l) = l2_ { (l.val, l.next) } else { (0, None)};

      let s = v1 + v2 + carry;
      let d = s % 10;
      carry = s / 10;

      result = Some(Box::new(ListNode{val: d, next: result}));
      l1_ = next_l1;
      l2_ = next_l2;
    }

    return reverse(result)

  }
//}