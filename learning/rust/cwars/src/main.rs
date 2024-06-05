use cwars::prime_streaming;

use crate::cwars::proper_fractions;


mod cwars {
    pub mod determinant;
    pub mod snail;
    pub mod expand;
    pub mod derpcode;
    pub mod balanced_ps;
    pub mod prime_streaming;
    pub mod proper_fractions;
}


fn main() {
    let test = "proper_fractions";

    if test == "determinant" {
        use cwars::determinant;
        // let mat = &[vec![1, 3],  vec![2,5]];
        let m33 = &[vec![2, 5, 3], vec![1, -2, -1], vec![1, 3, 4]];
        let det = determinant::determinant(m33);
        dbg!(det);
    } else if test == "snail" {
        use cwars::snail;

        let square = &[
            vec![1,2,3],
            vec![4,5,6],
            vec![7,8,9],
        ];
        let expected = vec![1, 2, 3, 6, 9, 8, 7, 4, 5];

        let ans = snail::snail(square);
        dbg!(&ans);
        assert_eq!(ans, expected);

        let square = &[
            vec![1,2,8,3],
            vec![4,5,8,6],
            vec![7,8,8,9],
            vec![4,3,2,1]
        ];
        let expected = vec![1,2, 8, 3, 6, 9, 1, 2, 3, 4, 7, 4, 5, 8, 8, 8];
        //  [1, 2, 8, 3, 3, 6, 9, 1, 2, 3, 4, 7, 4, 5, 8, 8, 8]
        let ans = snail::snail(square);
        dbg!(&ans);
        assert_eq!(ans, expected);

        let square = &[vec![1]];
        let expected = vec![1];

        let ans = snail::snail(square);

        dbg!(&ans);
        assert_eq!(ans, expected);

    } else if test == "expand" {
        use cwars::expand;

        let expr = "(x+1)^5";

        expand::expand(expr);
    } else if test == "derpcode" {
        use cwars::derpcode;

        // let h = "derp a-derp. derp derp herp derp herp derp derp derp herp a-derp a-derp a-derp a-derp a-derp. a-derp. herp a-derp.";
        let h = "derp a-derp. derp herp derp herp derp herp a-derp a-derp a-derp. derp derp derp derp derp derp herp derp herp a-derp a-derp a-derp. a-derp a-derp a-derp. a-derp. herp a-derp. herp a-derp herp a-derp derp derp derp derp herp derp derp derp herp. herp a-derp.";

        let out = derpcode::derpcode(h);
        dbg!(&h, &out);
        // assert_eq!(out, "d2");
        assert_eq!(out, "p0æs")
    } else if test == "balanced_ps" {
        use cwars::balanced_ps;

        let n = 4;
        let bps_4 = balanced_ps::balanced_parens(n);
        dbg!(bps_4);
    } else if test == "prime_streaming" {
        let mut cnt = 0;
        for p in prime_streaming::stream() {
            // println!("{p}");
            if p > 1_000_000 {
                break
            }
            cnt += 1
        }

        println!("cnt: {cnt}")
    } else if test == "proper_fractions"{
        let n = 12313145u64;
        let npf = proper_fractions::proper_fractions(n);
        println!("npf: {npf}")
    } else {
        panic!("Invalid value: test=`{test}`")
    }
}
