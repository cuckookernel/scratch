
pub fn longest_palindrome(s: String) -> String {
    let n = s.len();
    let arr = s.as_bytes();
    let mut max_seen = &arr[0..1];

    for i in 0..n {
        let (i, j) =  longest_odd_pal_at(arr, i);
        if (j - i) > max_seen.len() {
            max_seen = &arr[i..j]
        }
        if let Some((i, j))  = longest_even_pal_at(arr, i) {
            if (j - i) > max_seen.len() {
                max_seen = &arr[i..j]
            }
        }
    }

    let max_pal_u8 = max_seen.iter().map(|u|{*u}).collect::<Vec<_>>();
    return String::from_utf8(max_pal_u8)
           .expect("This should never happen as original string is guaranteed ascii")
}

pub fn longest_odd_pal_at(s: &[u8], i: usize) -> (usize, usize) {
    let n = s.len();

    let mut max_seen = (i, i+1);

    for j in 1..n {
        if (i < j) || (i + j >= n)  {break}
        if s[i-j] == s[i+j] {
            max_seen = (i-j, i+j+1)
        } else {
            break
        }
    }

    return max_seen
}


pub fn longest_even_pal_at(s: &[u8], i: usize) -> Option<(usize, usize)> {
    let n = s.len();
    let mut max_seen;

    if (i + 1) >= n || s[i+1] != s[i] {
        return None
    } else {
        max_seen = Some((i, i+2))
    }

    for j in 1..n {
        if (i < j) || (i + j + 2 >= n)  {break}
        if s[i - j] == s[i + j] {
            max_seen = Some((i - j, i + j + 2))
        } else {
            break
        }
    }

    return max_seen
}
