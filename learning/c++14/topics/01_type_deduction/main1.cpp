#include <iostream>
#include "type_name.h"

template<typename T, std::size_t N>
// full decl: constexpr std::size_t sz(T (&arr)[N]) {
//but arr is unused, so we drop it
constexpr std::size_t sz(T (&)[N]) {
    return N;
}


int main() {
    auto x = 27;
    const auto cx = x;
    const auto& rx = x;

    std::cout << "x: " << type_name<decltype(x)>() << std::endl;
    std::cout << "cx: " << type_name<decltype(cx)>() << std::endl;
    std::cout << "rx: " << type_name<decltype(rx)>() << std::endl;

    auto&& uref1 = x;
    std::cout << "uref1: " << type_name<decltype(uref1)>() << std::endl;

    auto&& uref2 = cx;
    std::cout << "uref2: " << type_name<decltype(uref2)>() << std::endl;

    auto&& uref3 = rx;
    std::cout << "uref3: " << type_name<decltype(uref3)>() << std::endl;

    auto&& uref4 = 42;
    std::cout << "uref4: " << type_name<decltype(uref4)>() << std::endl;

    int arr[10];
    std::cout << "Size of arr: " << sz(arr) << std::endl;

    int keyVals[] = { 1, 3, 7, 9, 11, 22, 35 };
    int mappedVals[sz(keyVals)];

    std::cout << "Size of mappedVals: " << sz(mappedVals) << std::endl;

    return 0;
}
