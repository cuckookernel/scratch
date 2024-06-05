use regex::{CaptureMatches, Regex};

pub fn expand(expr: &str) -> String {

    let re = Regex::new(r"\(([0-9-]*)([a-z])([+-])([0-9]+)\)\^([0-9]+)").unwrap();
    dbg!(&expr);

    let re_matches: CaptureMatches = re.captures_iter(expr);

    let mut pieces : Vec<String> = vec![];

    for re_match in re_matches {
        // in re_matches.map(|c:Captures| c.extract()) {  // works with regex version >= 1.0.0 perhaps

        let [a_str, var, sign_str, b_str, expo_str]
            = [1, 2, 3, 4, 5].map(|i| re_match.get(i).unwrap().as_str());
        // let (_s, [a_str, var, sign_str, b_str, expo_str]) = re_match;

        let a = if a_str == "" { 1i64 } else if a_str == "-" { -1i64 } else { a_str.parse::<i64>().unwrap()};
        let sign = if sign_str == "+" { 1 } else { -1 };
        let b: i64 = sign * b_str.parse::<i64>().unwrap();
        let n: u32 = expo_str.parse::<u32>().unwrap();

        for k in (0u32 .. n + 1u32).rev() {
            let n_k = n_choose_k(n.into(), k.into());
            // coef = (n choose k) * a^{n-k} * b^{k}
            let coef = n_k * a.pow(k.abs_diff(0)) * b.pow(n.abs_diff(k));

            // pieces.push(format!("{coef}{var}^{k}"));
            pieces.push(monom_to_str(coef, var, k, k == n));
        }
    }

    let ret =  pieces.join("");

    dbg!(&ret);
    return ret
}


pub fn n_choose_k(n: i64, k: i64) -> i64 {
    let mut numer = 1;
    let mut denom: i64 = 1;

    for i in 0 .. k {
        numer *= n - i;
        denom *= i + 1;
    }

    numer / denom
}

pub fn monom_to_str(coef: i64, var: &str, expo: u32, is_first: bool) -> String {
    if coef == 0 {
        return "".to_string()
    }

    let sign_pref = if is_first && coef > 0  { "" }
        else {
            if coef >= 0 {"+"} else {"-"}
        };
    let coef_abs = coef.abs();

    let expo_str =
        if expo == 1 {"".to_string()} else { format!("^{expo}") };

    if expo == 0 {
        return format!("{sign_pref}{coef_abs}")
    } else if coef == 1 {
        return format!("{sign_pref}{var}{expo_str}")
    } else if coef == -1 {
        return format!("{sign_pref}{var}{expo_str}")
    } else {
        return format!("{sign_pref}{coef_abs}{var}{expo_str}")
    }
}