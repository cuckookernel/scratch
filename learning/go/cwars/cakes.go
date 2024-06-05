package main

import (
	"math"
)

func Cakes(recipe, available map[string]int) int {
	ret := math.MaxInt32

	for k := range recipe {
		r_qty := recipe[k]
		qty, ok := available[k]
		if !ok {
			return 0
		}

		ret = min(ret, qty / r_qty)
	}
	return ret
}


func min(x, y int) int {
	if x <= y {
		return x
	} else {
		return y
	}
}
