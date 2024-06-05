package main

import (
	"fmt"

	"example.com/greetings"
)

func main() {
	result := greetings.Hello("Gladys")

	if !result.IsOk() {
		fmt.Println("Can't greet nobody..")
	} else {
		fmt.Println(result.Get())
	}
}