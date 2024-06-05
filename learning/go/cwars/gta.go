package main

import (
	"fmt"
	"strconv"
)


func Gta(limit int, numbers []int) int {
	numb_strs := []string {}
	max_len := 0
	for _, n := range numbers {
		n_str := strconv.Itoa(n)
		numb_strs = append(numb_strs, n_str)
		n_len := len(n_str)
		if n_len > max_len {
			max_len = n_len
		}
	}

	if max_len == 0 {
		return 0
	}

	base_list := buildBaseList(limit, numb_strs, max_len)
	fmt.Println("baseList:", base_list)

	if len(base_list) == 1 {
		return base_list[0]
	}

	num_arrays := num_arrays(len(base_list))
	sum := 0
	for _, d := range base_list {
		sum += d
	}
	return sum * num_arrays
}

func buildBaseList(limit int, numb_strs []string, max_len int) []int {
	seen := map[byte]int {}
	base_list := []int {}

	for i := 0; i < max_len; i++ {
		for _, n_str := range numb_strs {
			if i >= len(n_str) {
				continue
			}
			d_chr := n_str[i]
			if seen[d_chr] != 0 {
				continue
			} else {
				base_list = append(base_list, int(d_chr - '0'))
				seen[d_chr] = 1
			}

			if len(base_list) >= limit {
				return base_list
			}
		}
	}
	return base_list
}

func num_arrays(n int) int {
	num := 0
	for k := 1; k <= n; k++ {
		num += num_arrays_size(k, n)
	}
	//fmt.Println("num_arrays(", n, ") =", num);
	return num
}

func num_arrays_size(k, n int) int {
	// computes:  k * (n-1) * ... * (n - (k - 1))
	prod := k
	for i := 1; i <= k - 1; i++ {
		prod *= (n-i)
	}
	// fmt.Println("k: ", k, "n: ", n, " num_arrays(k, n): ", prod);
	return prod
}