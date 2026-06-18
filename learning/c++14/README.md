# C++17 Didactic Project

A self-teaching repository structured for learning **C++17** features topic by topic.

## Project Structure

- `CMakeLists.txt`: Root build configuration that enforces C++17 and common compiler warnings.
- `topics/`: Folder containing separate subfolders for each topic.
  - `01_type_deduction/`: Introduction to C++17 features (CTAD, Structured Bindings, inline variables, and `if constexpr`).
- `notes-on-effective-modern-c++.md`: Markdown notes file for tracking concepts, gotchas, and book summaries.

## Build and Run

To compile and run the project:

```bash
# 1. Create a build directory
mkdir -p build
cd build

# 2. Generate build files and compile
cmake ..
cmake --build .

# 3. Run a specific topic executable
./topics/01_type_deduction/01_type_deduction
```

## Adding a New Topic

1. Create a new directory under `topics/` (e.g. `topics/02_auto/`).
2. Add a `CMakeLists.txt` in that directory:
   ```cmake
   add_executable(02_auto main.cpp)
   ```
3. Add your `main.cpp` containing your code and experiments.
4. Register the new directory in the root `CMakeLists.txt` using the `add_topic` function:
   ```cmake
   add_topic(02_auto)
   ```
5. Re-run `cmake --build .` from your `build/` directory.
