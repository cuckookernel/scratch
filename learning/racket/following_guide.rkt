#lang racket

5
"Hello world!"

(define a "Hello world!")

(define (extract str)
  (define a 4)
  (substring str a 7))

(extract "Hellow!")

; (define (1 x) (printf x))

(define g 1)
(define (f c)
  (+ g c))
