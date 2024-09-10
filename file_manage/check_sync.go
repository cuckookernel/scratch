package main

import (
	"fmt"
	fs "io/fs"
	"os"
	fp "path/filepath"
)

// import "fmt"


func path_exists(path string) (bool, error) {
    _, err := os.Stat(path)
    if err == nil { return true, nil }
    if os.IsNotExist(err) { return false, nil }
    return false, err
}

type Counter struct {
	count int
}

func (cntr *Counter) find_one(_ string, _ fs.DirEntry, err error) error {
	if err == nil {
		cntr.count ++
		return fp.SkipAll
	}
	return nil
}

func is_empty(path string) (bool, error) {
   cntr := Counter {}
   err := fp.WalkDir(path, cntr.find_one)
   if err != nil {
	   return false, err
   }

   return cntr.count > 0, nil
}

type Checker struct {
	path_a string
	path_b string
}

func (ch *Checker) check_in_b(path string, d fs.DirEntry, err error) error {
	rel, _ := fp.Rel(ch.path_a, path)
	path_in_b := fp.Join(ch.path_b, rel)

	// fmt.Printf("path: `%v`, rel: `%v`\npath_in_b: `%v`\n", path, rel, path_in_b)

	exists, _ := path_exists(path_in_b)
	if !exists {
		fmt.Printf("NOT FOUND: %v\n", path_in_b)

	} else {
		fmt.Printf("FOUND: %v\n", path_in_b)
		os.Remove(path)
		the_dir := fp.Dir(path)
		is_empty_, err := is_empty(the_dir)
		if err != nil {
			return err
		}
		if is_empty_ {
			fmt.Printf("Dir is empty: %v\n", the_dir)
			os.Remove(the_dir)
		}
	}

	return nil
}


func main() {
	fmt.Println("check_sync started");

	checker := Checker { path_a: "/media/teo/WD-EXT", path_b: "/media/teo/T7" };

	fp.WalkDir(checker.path_a, checker.check_in_b)

}