const SPACE: &str = " ";
const DERP: &str = "derp";
const HERP: &str = "herp";
const A_DERP: &str = "a-derp";
const PRINT: &str = ".";


pub fn derpcode(commands: &str) -> String {
    let mut remainder = &commands["derp a-derp. ".len()..];
    dbg!(commands);

    let mut runner = Runner::default();
    // debugging: let mut instrs: Vec<&str> = vec![];
    loop {
        let shift_len =
            if remainder.starts_with(HERP) {
                runner.flip();
                HERP.len()
            } else if remainder.starts_with(DERP) {
                runner.inc();
                DERP.len()
            } else if remainder.starts_with(A_DERP) {
                runner.dec();
                A_DERP.len()
            } else if remainder.starts_with(SPACE) {
                // no-op
                SPACE.len()
            } else if remainder.starts_with(PRINT) {
                let should_stop = runner.print();
                if should_stop {
                    break
                }
                PRINT.len()
            } else {
                panic!("Unexpected start: {remainder}")
            };

        /* debugging:
        let last_instruction = &remainder[..shift_len];
        if last_instruction != " " { instrs.push(last_instruction)};
        let new_remainder = &remainder[shift_len..];
        let last_three =  if instrs.len() >= 3 { &instrs[instrs.len()-3..]} else { &instrs[..] };
        dbg!(last_three, last_instruction , &runner, new_remainder);
        */

        remainder = &remainder[shift_len..]
    }

    return runner.get_output();
}


#[derive(Default, Debug)]
struct Runner {
    curr_i: i32,
    cells: Vec<bool>,
    output: Vec<u8>
}

impl Runner {
    fn flip(&mut self) {
        if self.curr_i < 0 {
            panic!("Out of range flip, curr_i = {0}", self.curr_i)
        }
        let i_ = self.curr_i as usize;

        self.ensure_size(i_ + 1);
        self.cells[i_] = !self.cells[i_]
    }

    fn ensure_size(&mut self, s: usize)  {
        if s >= self.cells.len() {
            self.cells.resize(s, false)
        }
    }

    fn inc(&mut self) {self.curr_i += 1}
    fn dec(&mut self) {self.curr_i -= 1}

    fn print(&mut self) -> bool {
        if self.curr_i == -1 {
            return true
        }  else if self.curr_i >= 0 {
            let s: usize = self.curr_i as usize;
            let e = s + 8;
            self.ensure_size(e + 1);

            let bits = (s..e).map(|x| self.cells[x])
                .collect::<Vec<_>>();

            let new_byte = vec_to_u8(bits);
            self.output.push(new_byte);
            return false
        } else {
            panic!("Out of range print, curr_i = {0}", self.curr_i)
        }
    }

    fn get_output(&self) -> String {
        // String::from_utf8(self.out_chars.clone()).unwrap()

        let mut ret = String::new();
        self.output.iter().for_each(
            |&b| {
                let ch = std::char::from_u32(b.into()).unwrap();
                ret.push(ch)
            }
        );

        return ret;
    }
}

fn vec_to_u8(vec: Vec<bool>) -> u8 {
    let mut ret = 0u8;

    for (idx, bit) in vec.into_iter().enumerate() {
        ret |= (bit as u8) << (7 - idx)
    }

    return ret
}

