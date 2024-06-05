package utils

import (
	"errors"
)


type Result[T any] struct {
	value *T
	err   error
}

func Ok[T any](value T) Result[T] {
	return Result[T]{value: &value, err:nil}
}

/* func Error[T any](err error) Result[T] {
	return Result[T]{value: nil, err: err}
} */

func Error[T any](err string) Result[T] {
	return Result[T]{value: nil, err: errors.New(err)}
}

func (result Result[T]) IsOk() bool {
	return result.err == nil
}

func (result Result[T]) Get() *T {
	if result.err == nil {
		return result.value
	} else {
		panic("Attempted to get an error result")
	}
}
