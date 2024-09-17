open Base

let pylike_range ?(from=0) ?(step=1) (until: int) : int Sequence.t =
  Sequence.range ~stride:step ~start:`inclusive ~stop:`exclusive from until

let range_list ?(from=0) ?(step=1) (until: int) : int list =
  pylike_range ~from:from ~step:step until
  |> Sequence.to_list

let sum_int_list int_list = List.fold_left ~init:0 ~f:(+) int_list


let enumerate (a_list: 'a list): (int * 'a) list =
  let rec _enumerar (a_list: 'a list) (accum: (int * 'a) list) (i: int): (int * 'a) list =
      match a_list with
      | [] -> accum
      | x::xs -> _enumerar  xs ((i, x)::accum) (i+1)
  in
  _enumerar a_list [] 0 |> List.rev