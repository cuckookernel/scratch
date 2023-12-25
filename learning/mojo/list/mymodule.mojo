# from io import _Printable
# from IO import print_no_newline

@always_inline
fn min(a: Int, b: Int) -> Int:
    if a < b:
        return a
    else:
        return b


struct List[V: AnyType]:
    var data: Pointer[V]
    var size: Int
    var capacity: Int

    fn __init__(inout self):
        self.__init__(capacity=4)

    fn __init__(inout self, capacity: Int):
        self.size = 0
        self.capacity = capacity
        self.data = Pointer[V].alloc(self.capacity)

    fn __setitem__(inout self, i: Int, v: V) raises:

        if i < 0 or i >= self.size:
            raise Error("index of ouf range")

        self.data.store(i, v)

    fn __getitem__(self, i: Int) raises -> V:
        if i < 0 or i >= self.size:
            raise Error("index of ouf range")

        return self.data.load(i)

    fn append(inout self, v: V):

        if (self.size + 1) >= self.capacity:
            self._realloc(2 * (self.size + 1))

        self.data.store(self.size, v)
        self.size = self.size + 1

    fn _realloc(inout self, new_cap: Int):
        let new_data = Pointer[V].alloc(new_cap)

        let min_cap = min(self.capacity, new_cap)

        for i in range(0, min_cap):
            new_data.store(i, self.data.load(i))

        self.data.free()
        self.data = new_data
        self.capacity = new_cap


    fn __del__(owned self):
        self.data.free()


# fn show[V: _Printable](self: List[V]):
#    print_no_newline("[")
#    for i in range(self.size):
#        if i > 0:
#            print_no_newline(", ")
#        print_no_newline(self.data.load(i))
#    print("]")


fn main():
    let a = List[Int]()


