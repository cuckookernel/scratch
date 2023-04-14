#lang racket

(provide str)

; analog of str(x) in python
(define (str anything)
  (format "~a" anything))