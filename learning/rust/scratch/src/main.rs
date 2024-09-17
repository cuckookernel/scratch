struct Simple {
    a: i32,
}

impl Simple {
    pub fn mut_fun(&mut self) {
        self.a += 1
    }

    pub fn mut_fun2(&mut self) -> &i32 {
        self.a += 1;
        &self.a
    }
}

struct VRef<'a> {
    v: &'a [u32],
    i: i32,
}

impl<'a> VRef<'a> {
    pub fn mut_fun(&mut self) {
        self.i += 1;
    }

    pub fn mut_fun2(&mut self) -> impl Iterator<Item = u32> + 'a {
        self.i += 1;
        self.v.iter().map(|x| *x * 2)
    }

    pub fn mut_fun3(&'a mut self) -> impl Iterator<Item = u32> + 'a {
        self.i += 1;
        self.v.iter().map(|x| {
            self.i += 1;
            *x * 2
        })
    }

    pub fn mut_fun4<'b>(&'b mut self) -> impl Iterator<Item = u32> + 'b {
        self.i += 1;
        self.v.iter().map(|x| {
            self.i += 1;
            *x * 2
        })
    }
}

fn main() {
    let mut simp = Simple { a: 0 };

    simp.mut_fun();
    simp.mut_fun();

    println!("simp.a = {a}", a = simp.a);

    simp.mut_fun2();
    simp.mut_fun2();

    println!("simp.a = {a}", a = simp.a);

    let v = &[1, 3, 4];
    let mut vref = VRef { v, i: 0 };

    println!("vref.i = {}", vref.i);

    vref.mut_fun();
    vref.mut_fun();

    println!("vref.i = {}", vref.i);

    let iter1 = vref.mut_fun2();
    let iter2 = vref.mut_fun2();

    println!("vref.i = {}", vref.i);

    /*  This doesn't compile: Error: cannot borrow vref as mutable more than once
     let s1 = vref.mut_fun3().sum::<u32>();
     let s2 = vref.mut_fun3().sum::<u32>();
    */

    let s1 = vref.mut_fun4().sum::<u32>();
    let s2 = vref.mut_fun4().sum::<u32>();

    println!("vref.i = {}", vref.i);
}
