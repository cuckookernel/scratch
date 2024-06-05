pub fn balanced_parens(n: u16) -> Vec<String> {
    if n == 0 {
        return vec!["".to_string()];
    }

    let mut ret: Vec<String> = vec![];

    for i in 0..n {
        for bp_i in balanced_parens(i) {
            for bp_j in balanced_parens(n-i-1) {
                ret.push(format!("({bp_i}){bp_j}"))
            }
        }
    }
    return ret
}
