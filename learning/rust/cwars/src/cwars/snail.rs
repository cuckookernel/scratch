
pub fn snail(matrix: &[Vec<i32>]) -> Vec<i32> {
    let n = matrix.len();
    if n == 0 {
        return vec![]
    }

    let mut ret: Vec<i32> = Vec::<i32>::with_capacity(n * n);

    let half_n = if n % 2 == 0  { n / 2 } else { n / 2 + 1 };

    for i in 0 .. half_n {
        let part = snail_aux(matrix, i);
        ret.extend(part)
    }

    return ret;
}

fn snail_aux(matrix: &[Vec<i32>], i_start: usize) -> Vec<i32> {
    let n = matrix.len();
    let end = n - i_start;

    if i_start + 1 == end {
        return vec![matrix[i_start][i_start]]
    }

    let top_ref = matrix[i_start][i_start .. (end-1)].iter().map(|&i| i); //.collect::<Vec<_>>();
    let rig_ref = (i_start .. (end-1)).map(|r| matrix[r][end - 1]); //.collect::<Vec<_>>();
    let bot_ref = matrix[end - 1][(i_start + 1) .. end].iter().map(|&i| i).rev();
    let lef_ref = ((i_start + 1) .. end).map(|r| matrix[r][i_start]).rev();

    /*
    dbg!(top_ref.clone().collect::<Vec<_>>());
    dbg!(rig_ref.clone().collect::<Vec<_>>());
    dbg!(bot_ref.clone().collect::<Vec<_>>());
    dbg!(lef_ref.clone().collect::<Vec<_>>());
    */

    let chain =
        top_ref
        .chain(rig_ref)
        .chain(bot_ref)
        .chain(lef_ref);

    return chain.collect::<Vec<_>>();
}