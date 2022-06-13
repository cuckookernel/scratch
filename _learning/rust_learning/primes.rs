struct Primes {
    up_to: usize,
    sieve: Vec<bool>,
    current: usize
}

impl Primes {
    fn new(up_to: u64) -> Primes {

        let up_to_ = up_to as usize;
        let mut sieve = vec![true; up_to_ + 1];
        sieve[0] = false;
        sieve[1] = false;

        Primes {
            up_to: up_to_,
            sieve,
            current: 0
        }
    }
}

impl Iterator for Primes {
    type Item = u64;

    fn next(&mut self) -> Option<u64> {
        while self.current <= self.up_to as usize && !self.sieve[self.current] {
            self.current += 1;
        }

        if self.current > self.up_to {
            None
        } else {
            // prime found, mark multiples as long as prime <= sqrt(up_to)
            let prime = self.current;

            if prime * prime <= self.up_to {
                // println!("{} {}", prime, self.up_to / prime);
                for k in 2 .. (self.up_to / prime + 1) {
                    self.sieve[prime * k] = false;
                    // println!("discarded: {} {}", prime, prime * k);
                }
            }

            self.current += 1;

            Some(prime as u64)
        }
    }
}

#[derive(Debug)]
struct PrimePower{
    // represents p^alpha
    p: u64,
    alpha: u32
}

fn prime_factorize_0( n: u64 ) -> Vec<PrimePower> {
    let mut ret: Vec<PrimePower> = Vec::new();

    let mut remaining = n;

    for p in Primes::new(n) {
        if remaining % p == 0 {
            let mut pp = PrimePower{p, alpha: 0};

            while remaining % p == 0 {
                pp.alpha += 1;
                remaining /= p;
            }
            ret.push( pp )
        }
    }

    ret
}

fn is_prime(n: u64) -> bool {
    let sqrt_n = (n as f64).sqrt() as u64;

    if n < 2 {
        false
    }
    else {
        for p in Primes::new(sqrt_n) {
            if n % p == 0 {
                return false
            }
        }
        return true
    }
}

fn prime_factorize( n: u64 ) -> Vec<PrimePower> {
    let mut ret: Vec<PrimePower> = Vec::new();

    let mut remaining = n;

    let sqrt_n = (n as f64).sqrt() as u64;

    for p in Primes::new(sqrt_n) {
        if remaining % p == 0 {
            let mut pp = PrimePower{p, alpha: 0};

            while remaining % p == 0 {
                pp.alpha += 1;
                remaining /= p;
            }
            ret.push( pp )
        }
    }

    if remaining > 1 {
        ret.push( PrimePower{p: remaining, alpha: 1} )
    }

    ret
}


fn sum_divisors_squared(n: u64) -> u64 {
    let pf = prime_factorize(n);
    println!("{:?}", pf);

    // pf.iter().map( |PrimePower{p,alpha}| (p.pow(2 * (alpha+1)) - 1)/(p*p - 1) ).product()
    pf.iter().map( |PrimePower{p,alpha}| sum_pows(p*p, *alpha) ).product()
}

fn sum_pows(p2: u64, k: u32) -> u64 {
    (0 .. (k+1)).map ( |a| p2.pow(a) ).sum()
}


fn sum_divisors_squared_slow(n: u64) -> u64 {
    (1..(n+1)).map( |d| if n % d == 0 { d*d } else { 0 } ).sum()
}


fn retrieve_num(pf: &Vec<PrimePower>) -> u64 {
    let mut prod = 1;

    for pp in pf.iter() {
        prod *= pp.p.pow( pp.alpha )
    }

    prod
}

fn test_sum_divisors() -> bool {
    for i in 1..1000 {
        // let pf = prime_factorize(i);
        // let prod = retrieve_num( &pf );
        let sum_div2 = sum_divisors_squared(i);
        let sum_div2_slow = sum_divisors_squared_slow(i);

        if sum_div2 != sum_div2_slow {

            println!("{} {} {:?}", i, sum_div2, sum_div2_slow );

            let pf = prime_factorize(i);
            println!("{:?}", pf)
        }
    }
    true
}

fn test_prime_factorize_1(n: u64) -> bool {

    let pf2 = prime_factorize(n);
    let n2 = retrieve_num(&pf2);

    if n2 != n {
        println!("bad product {} {} {:?}", n, n2, pf2);
        false
    }
    else {
        for pp in pf2.iter() {
            if !is_prime(pp.p) {
                println!("not prime: {} n:{} pf: {:?}", pp.p, n, pf2);
                return false;
            }
        }
        true
    }
}

fn test_prime_factorize(n: u64) -> bool {
    let mut error_cnt = 0;

    for  k in 1..n {
        // let pf1 = prime_factorize(n);
        error_cnt += if !test_prime_factorize_1(k) {1} else {0};
    }

    if error_cnt > 0 {
        println!("error_cnt: {}", error_cnt);
        false
    } else {
        println!("Everything ok!");
        true
    }
}

fn list_squared(m: u64, n: u64) -> Vec<(u64, u64)> {
    let mut ret: Vec<(u64, u64)> = Vec::new();
    println!("\nm: {} n:{}", m, n);

    for k in m..n {
        let d2_sum = sum_divisors_squared(k);
        let d2_sum_sqrt = (d2_sum as f64).sqrt() as u64;

        if d2_sum == d2_sum_sqrt.pow(2) {
            println!("{:?} {}", k, d2_sum);
            ret.push( (k, d2_sum) )
        }
    }
    // let primes: Vec<u64> =  Primes::new(1000).collect();
    // println!("{:?}", primes);

    return ret;
}

fn test_switch(n: u8) -> bool{
    match n {
        1 => test_sum_divisors(),
        2 => test_prime_factorize_1(13123),
        3 => test_prime_factorize(13123),
        _ => false
    }
}

fn main() {
    // let primes: Vec<u64> = Primes::new(100000).collect();
    // println!("{} {:?}", primes.len(), primes)

    // let i = 55;

    // test_prime_factorize();
    // test_prime_factorize(10000);
    // list_squared(530005, 530008);
    // sum_divisors_squared(530005);
    println!( "{}", sum_divisors_squared(530006)) ;
    // sum_divisors_squared(530007);

}


// m: 530000 n:550000
