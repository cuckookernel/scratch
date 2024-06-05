package main

import "fmt"

func NbDig(n int, d int) int {
    d_chr := rune(fmt.Sprint(d)[0])

	cnt := 0
	for k := 0; k <= n; k ++ {
		a_str := fmt.Sprint(k*k)

		for _, a_chr := range a_str {
			if a_chr == d_chr { cnt++ }
		}
	}
	return cnt
}
