package main

import (
	"unicode"
)

func toWeirdCase(str string) string {
	// Your code here and happy coding!
	var out [] rune

	c := 0

	for i := 0; i < len(str); i+=1 {
	    if str[i] == ' ' {
			c = 0
			out = append(out, rune(' '))
			continue
		}
		var ch rune = rune(str[i])

	  var out1 rune
	  if c % 2 == 0 {
	    out1 = unicode.ToUpper(ch)
	  } else {
	    out1 = unicode.ToLower(ch)
	  }
	  out = append(out, out1)
	  c += 1
	}

	return string(out)
}