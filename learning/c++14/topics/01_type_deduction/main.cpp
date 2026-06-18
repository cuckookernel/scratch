#include <iostream>
#include <memory>
#include <type_traits>
#include <string>
#include <utility>

// 1. C++14: Return type deduction
// The compiler automatically deduces the return type as int.
auto add(int a, int b) {
    return a + b;
}

// 2. C++14: Variable template
template<typename T>
constexpr T pi = T(3.1415926535897932385L);

// 3. C++17: Inline variable (allows definition in header files without linker errors)
inline constexpr double PI_17 = 3.14159265358979323846;

// 4. C++17: if constexpr (compile-time conditional evaluation)
template<typename T>
auto get_value(T x) {
    if constexpr (std::is_pointer_v<T>) {
        return *x; // Evaluated at compile-time only if T is a pointer
    } else {
        return x;
    }
}

int main() {
    std::cout << "=========================================\n";
    std::cout << "       C++17 Didactic Project Started    \n";
    std::cout << "=========================================\n\n";

    // Test C++14 Auto Return Type Deduction
    auto sum = add(10, 20);
    std::cout << "[1] C++14 Auto Return Type Deduction:\n";
    std::cout << "    add(10, 20) = " << sum << "\n\n";

    // Test C++14 Generic Lambdas
    auto print_value = [](const auto& label, const auto& val) {
        std::cout << "    " << label << ": " << val << "\n";
    };

    std::cout << "[2] C++14 Generic Lambdas:\n";
    print_value("Integer value", 42);
    print_value("Double value", 3.14159);
    print_value("String value", std::string("Hello C++"));
    std::cout << "\n";

    // Test C++14 Variable Templates
    std::cout << "[3] C++14 Variable Templates:\n";
    std::cout << "    pi<double> = " << pi<double> << "\n";
    std::cout << "    pi<float>  = " << pi<float> << "\n\n";

    // Test C++14 std::make_unique
    std::cout << "[4] C++14 std::make_unique:\n";
    auto ptr = std::make_unique<int>(1337);
    std::cout << "    Value in unique_ptr: " << *ptr << "\n\n";

    // Test C++17 Inline Variables
    std::cout << "[5] C++17 Inline Variables:\n";
    std::cout << "    PI_17 = " << PI_17 << "\n\n";

    // Test C++17 Class Template Argument Deduction (CTAD)
    std::pair p(42, std::string("C++17 CTAD"));
    std::cout << "[6] C++17 Class Template Argument Deduction (CTAD):\n";
    std::cout << "    Deduces std::pair types automatically.\n\n";

    // Test C++17 Structured Bindings
    auto [id, message] = p;
    std::cout << "[7] C++17 Structured Bindings:\n";
    std::cout << "    id = " << id << "\n";
    std::cout << "    message = " << message << "\n\n";

    // Test C++17 if constexpr
    std::cout << "[8] C++17 if constexpr:\n";
    int val = 1337;
    int* val_ptr = &val;
    std::cout << "    get_value(val)     = " << get_value(val) << "\n";
    std::cout << "    get_value(val_ptr) = " << get_value(val_ptr) << "\n\n";

    // Test C++17 Initializer in if-statement
    std::cout << "[9] C++17 Initializer in if-statement:\n";
    if (auto status = add(5, 5); status > 5) {
        std::cout << "    Status is " << status << " (greater than 5)\n";
    }

    std::cout << "\n=========================================\n";
    return 0;
}
