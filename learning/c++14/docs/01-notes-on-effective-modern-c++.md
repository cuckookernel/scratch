
# TODO:


- auto
    - type deduction: declaring variables with auto
        - example: auto i = 0; (i is int)
        - example: auto* p = &i; (p is int*)
        - example: auto& r = i; (r is int&)
        - example: auto&& u = i; (u is int&)
        - example: auto&& v = 42; (v is int&&)

        - If the initializer is a reference, the reference type is dropped
            - auto& arr = array; // arr is int* (not int&, because array is a reference to an array)

    - generic lambdas: lambada parameter types declared as auto (filled in on every call site?)
    - return type deduction:  return type declared as auto, inferred by compiler

- decltype
- decltype(auto)


- std::unique_ptr, std::make_unique
- std::shared_ptr

- Const member functions should be thread safe.
- Avoid default capture modes in lambdas.

- Differences between std::atomic and volatile.

- typename to declare type parameers in templates (the standards uses `class` instead)

- copy-constructed copy vs move-constructed copy (p. 4)
- std::move

- concurrency primitives in C++
- noexcept (in function declarations)
- std::weak_ptr (Item 20)

- Universal references (a.k.a forwarding references) (Item 24)
    - std::forward


## Old vs new

| Old Way | New Way |
| --- | --- |
| `0` or `NULL` (as null pointer) | `nullptr` |
| `typedef` | Alias declarations (`using`) |
| `std::auto_ptr` (deprecated/removed) | `std::unique_ptr` |
| Built-in static arrays | `std::array` |

- New way:
    - auto declarations
    - enums should be scope
    - smart pointers are now preferable to built-in ones
    - moving objects is normally better than copying them
    - range based for loops
    - lambda expressions
    - use brace initialization for everything
    - rvalue references


## Rvalue vs lvalues

-  in concept: rvalues correspond to temporary objects returned fromfunctions, while l values correspond to objects you can refer to, either by name or by following a pointer or lvalue reference.

- Heuristic: if you can take the address of an expression, it's an lvalue. Otherwise it's an rvalue
- All parameters are lvalues.

- Copies of rvalues are generally move constructed, while copies of lvalues are usually copy constructed.

Expressions passed at the call site are function's arguments.
The arguments are used to initialize the function's parameters.

The distinction beteween rvalues and lvalues matters because parameters are lvalues, but
the arguments with which they are initialize may be rvalues or lvalues. This is relevant in
the process of perfect forwarding, whereby an argument passed to a function is passed to a second functon such that the argument's rvalueness or lvalueness is preserved.


## Exception safety

Well-designed functions
Exception safety guarantee (basic guarantee): even if exceptions is thrown, program invariants remain intact,no data structures are corrupted, and no resources are leaked.

strong guarantee: if exception arised the state of the program remains as it was prior to the call.


## Type deduction for templates


Because array parameter declarations are treated as if they were pointer parameters, the type of an array that's passed to a template function by value is deduced to be a pointer type.

However! Although functions can't declare parameters that are truly arrays they can declare parameters that are references to array.


```cpp
template<typename T, std::size_t N>
constexpr std::size_t sz(T (&arr)[N]) {
    return N;
}
```


Things to Remember

- During template type deduction, arguments that are references are treated as non-references, i.e., their reference-ness is ignored.

- When deducing types for universal reference parameters, lvalue arguments get special treatment.

- When deducing types for by-value parameters, const and/or volatile arguments are treated as non-const and non-volatile.

- During template type deduction, arguments that are array or function names decay to pointers, unless they’re used to initialize references.
