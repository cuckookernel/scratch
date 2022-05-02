impl Solution {
    pub fn my_atoi(s: String) -> i32 {

        let mut pos_part: i64 = 0;
        let mut sign: i64 = 1;
        let mut at_beginning = true;

        // println!( "\n\n === {}", s);
        for ch in s.chars() {
            match ch {
                ' ' =>
                    if at_beginning {
                        continue;
                    } else {
                        break;
                    },
                '+'|'-' =>
                    {

                        if at_beginning {
                            match ch {
                                '+' => sign = 1,
                                '-' => sign = -1,
                                _ => break // never actually happens
                            }
                        } else {
                            break;
                        }
                        at_beginning = false;
                    },
                '0'..='9' => {
                    at_beginning = false;
                    pos_part = pos_part * 10 + (ch as u8 - '0' as u8) as i64
                },
                _ => {
                    break;
                }


            } // end match ch

            // println!( "{} sign={} pos_part={}", ch, sign, pos_part);

            if sign * pos_part >= (i32::MAX) {
                return i32::MAX
            } else if sign * pos_part <= (i32::MIN as i64) {
                return i32::MIN
            }

        } // end for ch


        if sign * pos_part >= (i32::MAX as i64) {
            i32::MAX
        } else if sign * pos_part <= (i32::MIN as i64) {
            i32::MIN
        } else {
            (sign * pos_part) as i32
        }
    }

}