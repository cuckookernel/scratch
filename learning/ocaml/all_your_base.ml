open Base

type base = int

let pylike_range ?(from=0) ?(step=1) (until: int) : int Sequence.t =
    Sequence.range ~stride:step ~start:`inclusive ~stop:`exclusive from until

  let range_list ?(from=0) ?(step=1) (until: int) : int list =
    pylike_range ~from:from ~step:step until
    |> Sequence.to_list

  let sum_int_list int_list = List.fold_left ~init:0 ~f:(+) int_list


let to_int ~from ~digits : int =
    let rev_digits = List.rev digits in
    let exponents = range_list (List.length digits) in
    let dig_exp_pairs = List.zip_exn rev_digits exponents in
    sum_int_list @@ List.map dig_exp_pairs ~f:(fun (d, e) -> d * from ** e)

let rec to_base_0 (target:int)  (n:int) (accum: int list): int list =
    if n = 0 then
        if List.length accum = 0 then [ 0 ] else accum
    else
        let r : int = n % target in
        let next_n: int = (n - r) / target in
        to_base_0 target next_n (r :: accum)

let convert_bases_0 ~from ~digits ~target =
    let n = to_int ~from ~digits in
    to_base_0 target n []

let convert_bases ~from ~digits ~target =
    if from <= 1 then
        None
    else if target <= 1 then
        None
    else
        Some( convert_bases_0 ~from ~digits ~target )
