package main

import (
	"fmt"
	"strings"
)

func DuplicateEncode(word string) string {

	word_ := strings.ToLower(word)
	cnts := make(map[byte] int);

	for i := 0; i < len(word_); i += 1 {
		ch := word_[i]
		value, ok := cnts[ch]

		if ok {
			cnts[ch] = value + 1
		} else {
			cnts[ch] = 1
		}
	}

	var out []byte;
	for i := 0; i < len(word_); i += 1 {
		if cnts[word_[i]] > 1 {
			out = append(out, ')')
		} else {
			out = append(out, '(')
		}
	}

	return string(out)
}


func Scratch() {
	var b1 bool = true;
	var b2 bool = false;

	b3 := b1 && b2

	fmt.Print(b3)

}
