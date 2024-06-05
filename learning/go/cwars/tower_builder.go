package main

import "strings"

func TowerBuilder(nFloors int) []string {

	var out = []string{}

	for i := 1; i <= nFloors; i++ {
		margin := strings.Repeat(" ", nFloors - i)
		center := strings.Repeat("*", 2 * i - 1)
		floor := strings.Join([]string{margin, center,margin}, "")
		out = append(out, floor)
	}

	return out
}
