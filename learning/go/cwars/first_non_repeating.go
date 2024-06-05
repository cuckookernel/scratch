package main

import "unicode"

func FirstNonRepeating(str string) string {
	counts := map[rune]int {}

	for _, ch := range str {
		ch = unicode.ToLower(ch)
		cnt := counts[ch]
		counts[ch] = cnt + 1
	}
	for _, ch := range str {
		ch_ := unicode.ToLower(ch)
		if counts[ch_] == 1 {
			return string(ch)
		}
	}

	return ""
}