
1. What is the difference between traits `PartialEq` and `Eq`?

`PartialEq` means equality comparison is a partial equivalence relation (
    satisfies transitivity, and symmetry but might not satisfy reflexivity)
`Eq` means equality comparison is a (full) equivalence relation (reflexivity, transitivity, symmetry)

Example of a type that is `PartialEq` but not `Eq` are floating point numbers since it is `NaN == NaN` is `false`.

In both cases the method that has to be implemented for the type `T` has the signature `fn eq(&self, a: &T)`


2. What are the different function traits?

3. How to make an implementation of a function trait for struct?
