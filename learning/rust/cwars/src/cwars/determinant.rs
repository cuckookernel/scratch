
pub fn determinant(matrix: &[Vec<i64>]) -> i64 {
    let n = matrix.len();
    let row_idxs = (0..n).collect::<Vec<_>>();
    return determinant_(matrix, &row_idxs)
}

fn determinant_(matrix: &[Vec<i64>], col_idxs: &Vec<usize>) -> i64 {
    let dim = col_idxs.len();
    assert!(dim > 0);

    if dim == 1 {
        return matrix[0][col_idxs[0]]
    } else {
        let mut ret: i64 = 0;

        for i in 0..col_idxs.len() {
            let col_idx = col_idxs[i];

            let a = matrix[0][col_idx];
            if  a != 0 {
                // let row_idxs1 = all_but_ith(row_idxs, idx);
                let col_idxs1: Vec<usize> = col_idxs.iter()
                        .filter(|idx1| {col_idx != **idx1})
                        .map(|i| {*i}).collect();
                let minor = determinant_(&matrix[1..], &col_idxs1);
                let sign = if i % 2 == 0 {1} else {-1};
                ret += a * sign * minor
            }

        }

        return ret
    }
}
