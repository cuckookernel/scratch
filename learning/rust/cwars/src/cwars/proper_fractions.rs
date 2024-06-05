use std::{collections::HashMap};

use super::prime_streaming::{self as ps, PrimeStreamer};


pub fn proper_fractions(n: u64) -> u64 {
    let pf = prime_factorize(n);

    let mut ret = 1u64;
    for (p, alpha) in pf.factorization {
        ret *= p.pow(alpha) - p.pow(alpha - 1)
    }

    return ret
}

pub fn prime_factorize(n: u64) -> PartialFactorization {
    let factorization = HashMap::<u64, u32>::new();
    let mut ret = PartialFactorization{
        factorization,
        unfactored: n,
        prime_streamer: PrimeStreamer::new()
    };

    while ret.unfactored != 1 {
        ret.make_progress()
    }

    let fctr = &ret.factorization.iter().collect::<Vec<_>>();
    println!("Prime factorization: {fctr:?}");
    return ret
}

pub struct PartialFactorization {
    factorization: HashMap<u64, u32>,
    unfactored: u64,
    prime_streamer: ps::PrimeStreamer
}

impl PartialFactorization {
    fn make_progress(&mut self) {
        if self.unfactored == 1 {
            return
        }

        if let Some(p) = self.prime_streamer.next() {
            let p64 = p as u64;

            if (p as f64) >= (self.unfactored as f64).sqrt() + 1. {
                self.factorization.insert(self.unfactored, 1);
                self.unfactored = 1
            }

            while self.unfactored % p64 == 0 {
                if let Some(v) = self.factorization.get_mut(&p64) {
                    *v += 1
                } else {
                    self.factorization.insert(p64, 1);
                }
                self.unfactored /= p64
            }
        } else {
            panic!("Ran out of primes?!")
        }
    }
}

