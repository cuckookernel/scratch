package main

import (
	"math"
)

func HighestRank(nums []int) int {
	cnts := map[int]int {}

	for _, n := range nums {
		cnts[n] = cnts[n] + 1
	}

	// fmt.Println("cnts:", cnts)

	ret := math.MinInt32
	max_cnt := math.MinInt32
	for n := range cnts {
		//fmt.Println("- n:", n, "cnts[n]:", cnts[n])
		if (cnts[n] > max_cnt) ||  ((cnts[n] == max_cnt) && (n > ret)) {

			ret = n
			max_cnt = cnts[n]
			// fmt.Println("ret:", n, "max_cnt:", max_cnt)
		}
	}

	return ret
}