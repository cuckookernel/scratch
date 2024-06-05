package main


func FindUniq(arr []float32) float32 {
	cnts := map[float32]int{}
	for _, x := range arr {
		cnts[x] = cnts[x] + 1
	}

	for x := range cnts {
		if cnts[x] == 1 {
			return x
		}
	}

	return 0.0 // should never happen
}