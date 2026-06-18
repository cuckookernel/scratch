use std::env;
use std::fs::File;
use std::io::{self, BufReader, BufWriter, Write};

// mod hr_helpers;

mod hrh {
    use std::fmt::Debug;
    use std::io::BufRead;
    use std::str::FromStr;

    pub fn read_line_as<T: FromStr>(reader: &mut dyn BufRead) -> T
    where
        <T as FromStr>::Err: Debug,
    {
        let mut t_temp = String::new();
        reader.read_line(&mut t_temp).unwrap();
        t_temp.trim().parse().unwrap()
    }

    pub fn read_line_as_vec<T: FromStr>(reader: &mut dyn BufRead) -> Vec<T>
    where
        <T as FromStr>::Err: Debug,
    {
        let mut t_temp = String::new();
        reader.read_line(&mut t_temp).unwrap();

        t_temp
            .split(' ')
            .into_iter()
            .map(|s| s.trim().parse().unwrap())
            .collect()
    }
}

#[allow(dead_code)]
fn example_read_to_stdin_write_to_output_path() {
    // read to stdin an
    let output_path = env::var("OUTPUT_PATH").unwrap_or("data/out.txt".into());
    let mut fout = File::create(output_path).expect("Failed to create output file");

    let stdin = io::stdin();
    let mut reader = BufReader::new(stdin.lock());
    let n: usize = hrh::read_line_as(&mut reader);

    for line_num in 0..n {
        let s: String = hrh::read_line_as(&mut reader);
        let i: i32 = hrh::read_line_as(&mut reader);
        let vi: Vec<i32> = hrh::read_line_as_vec(&mut reader);
        let vf: Vec<f32> = hrh::read_line_as_vec(&mut reader);

        // let y = max_xor_value(&s, k);

        writeln!(fout, "{} {} {} - {:?} - {:?}", line_num, s, i, vi, vf).unwrap();
    }
}

fn example_read_to_stdin_write_to_stdout() {
    // read to stdin an
    let stdout = io::stdout();
    let mut fout = BufWriter::new(stdout.lock());

    let stdin = io::stdin();
    let mut reader = BufReader::new(stdin.lock());
    let n: usize = hrh::read_line_as(&mut reader);

    for line_num in 0..n {
        let s: String = hrh::read_line_as(&mut reader);
        let i: i32 = hrh::read_line_as(&mut reader);
        let vi: Vec<i32> = hrh::read_line_as_vec(&mut reader);
        let vf: Vec<f32> = hrh::read_line_as_vec(&mut reader);

        // let y = max_xor_value(&s, k);

        writeln!(fout, "{} {} {} - {:?} - {:?}", line_num, s, i, vi, vf).unwrap();
    }
}

fn main() {
    // example_read_to_stdin_write_to_output_path();
    example_read_to_stdin_write_to_stdout();
}
