#lang br/quicklang

(require "fpy-reader.rkt")

(define the-program
  "def f(x:Int) = {
_ab = b9
   g(3)
   k()
   }")

#;(define parsed-program
  (parse
   (make-tokenizer
    (open-input-string the-program))))

(define tokenize
  (make-tokenizer
    (open-input-string the-program)))

(define (get-all-tokens)
  (for/list ([i (in-range 100)])
    (tokenize)))


(require brag/support)
(require parser-tools/lex-sre)
  
#;(define parsed-program
  (parse
   (make-tokenizer
    (open-input-string the-program))))

(define parse-tree
    (parse ".test" (make-tokenizer
                     (open-input-string the-program))))

parse-tree
#;(define all-tokens
  (define token (tokenizer))
  (if (eq? token )
  ))
