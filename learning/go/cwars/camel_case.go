package main

import (
	"bytes"
	"regexp"
	"strings"
)

func ToCamelCase(s string) string {
	regex := regexp.MustCompile("[^A-Za-z]")

	parts := regex.Split(s, -1)

	out := []string{};

	for i, part := range parts {

		var out1 string;
		if i == 0 {
			out1 = part
		} else {
			out1 = firstCapitalized(part)
		}
		out = append(out, out1)
	}

	return strings.Join(out, "")
}

func firstCapitalized(s string) string {
	return string(bytes.ToUpper([]byte{s[0]})) + s[1:]
}
