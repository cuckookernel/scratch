from list import List


from algorithm.functional import map


fn print(a: List[Int]):
    print_no_newline('[')
    for i in range(a.size):
        print_no_newline(a.data.load(i))
        if i + 1 < a.size:
            print_no_newline(', ')
    print_no_newline(']')


fn main():
    var a = List[Int]()
    a.append(3)
    a.append(4)
    print(a)
    print(a.size)
    print(a.capacity)
    print_no_newline()