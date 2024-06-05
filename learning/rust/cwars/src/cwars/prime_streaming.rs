const SOME_PRIMES: &[u32;9] = &[2u32, 3u32, 5u32, 7u32, 11u32, 13u32, 17u32, 19u32, 23u32];

pub struct PrimeStreamer {
    curr: u32
}

impl PrimeStreamer {
    pub fn new() -> PrimeStreamer {
        return PrimeStreamer{curr:2}
    }
}

impl Iterator for PrimeStreamer {
    type Item = u32;

    fn next(&mut self) -> Option<<Self as Iterator>::Item> {
        loop {
            if is_prime(self.curr) {
                let ret = self.curr;
                self.curr += 1;
                return Some(ret)
            } else {
                self.curr +=1;
            }
        }
    }
}

fn is_prime(n: u32) -> bool {
    for d in SOME_PRIMES {
        if *d >= n { break }
        if n % *d == 0 { return false }
    }

    let sqrt_n = (n as f64).sqrt().ceil() as u32;
    for d in 24..(sqrt_n + 1) {
        if d % 2 == 0 { continue }
        if n % d == 0 { return false }
    }

    return true
}

pub struct PrimeStreamer2 {
    curr: u64,
    primes: Vec<u64>
}

impl Iterator for PrimeStreamer2 {
    type Item = u64;

    fn next(&mut self) -> Option<<Self as Iterator>::Item> {
        loop {
            if is_prime2(self.curr, &self.primes) {
                let ret = self.curr;
                self.curr += 1;
                self.primes.push(ret);
                return Some(ret)
            } else {
                self.curr +=1;
            }
        }
    }
}

fn is_prime2(n: u64, primes: &Vec<u64>) -> bool {
    for p in primes {
        if *p >= n { break }
        if n % *p == 0 { return false }
    }

    let sqrt_n = (n as f64).sqrt().ceil() as u64;
    let max_prime = primes[primes.len() - 1];
    for d in (max_prime + 2)..(sqrt_n + 1) {
        if d % 2 == 0 { continue }
        if n % d == 0 { return false }
    }

    return true
}

pub fn stream() -> impl Iterator<Item = u32> {
    PrimeStreamer{curr:2}
}

pub fn stream2() -> impl Iterator<Item = u64> {
    PrimeStreamer2{curr:2, primes: vec![2, 3, 5, 7]}
}