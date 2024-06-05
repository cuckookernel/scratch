package greetings

import (
	"fmt"

	. "example.com/utils"
)


func Hello(name string) Result[string] {
	if name == "" {
		return Error[string]("no name given")
	}

	var message string = fmt.Sprintf("Hi, %v. Welcome!", name)
	return Ok(message)
}