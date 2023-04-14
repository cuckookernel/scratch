#lang racket


(define (sum x y)
  (define a 5)
  (+ x y a))

(display (sum 1 3))
