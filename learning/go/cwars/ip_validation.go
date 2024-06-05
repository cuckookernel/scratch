package main

import (
	"regexp"
	"strconv"
	"strings"
)

func Is_valid_ip(ip string) bool {
	parts := strings.Split(ip, ".")

	if len(parts) != 4 {
		return false
	}

	for _, part := range parts {
		val, _ := strconv.Atoi(part)
		if !(val >= 0 && val < 256) {
			return false
		}
	}

	return true
}

func Is_valid_ip_2(ip string) bool {
	regex := regexp.MustCompile(`^(0|([1-9]\d*))\.(0|([1-9]\d*))\.(0|([1-9]\d*))\.(0|([1-9]\d*))$`)
	matches := regex.FindStringSubmatch(ip)

	if len(matches) != 9 {
		return false
	}

	// fmt.Println(matches)

	for i := 0; i < 4; i++  {
		m := matches[2*i + 1]
		val, _ := strconv.Atoi(m)

		if !(val >= 0 && val < 256) {
			return false
		}
	}

	return true
}