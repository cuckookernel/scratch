use std::fmt::Debug;
use std::io::BufRead;
use std::str::FromStr;

#[allow(dead_code)]
pub fn read_line_as<T: FromStr>(reader: &mut dyn BufRead) -> T
where
    <T as FromStr>::Err: Debug,
{
    let mut t_temp = String::new();
    reader.read_line(&mut t_temp).unwrap();
    t_temp.trim().parse().unwrap()
}

#[allow(dead_code)]
pub fn read_line_as_vec<T: FromStr>(reader: &mut dyn BufRead) -> Vec<T>
where
    <T as FromStr>::Err: Debug,
{
    let mut t_temp = String::new();
    reader.read_line(&mut t_temp).unwrap();

    t_temp
        .split(' ')
        //.into_iter()
        .map(|s| s.trim().parse().unwrap())
        .collect()
}
