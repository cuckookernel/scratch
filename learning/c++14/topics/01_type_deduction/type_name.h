#include <string_view>

template <typename T>
constexpr std::string_view type_name() {
    std::string_view name;
    std::string_view prefix;
    std::string_view suffix;

#if defined(__clang__) || defined(__GNUC__)
    name = __PRETTY_FUNCTION__;
    //std::cout << "__PRETTY_FUNCTION__: " << name << std::endl;
    if (name.find("[with T = ") != std::string_view::npos) {
        prefix = "[with T = "; // GCC format
    } else {
        prefix = "[T = ";      // Clang format
    }
    suffix = "; std::string_view = std::basic_string_view<char>]";
#elif defined(_MSC_VER)
    name = __FUNCSIG__;
    prefix = "type_name<";
    suffix = ">(void)";
#else
    return "Unsupported Compiler";
#endif

    std::size_t start = name.find(prefix);
    if (start == std::string_view::npos) return "Unknown Type";
    start += prefix.size();

    std::size_t end = name.rfind(suffix);
    if (end == std::string_view::npos || end < start) return "Unknown Type";

    return name.substr(start, end - start);
}
