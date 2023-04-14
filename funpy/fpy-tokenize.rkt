#lang br/quicklang
(require "fpy-lexer.rkt")
(require "util.rkt")

(provide read-syntax make-tokenizer quote)

(define (read-syntax path port)
  (define tokenize (make-tokenizer port))
  (for/list ([tok (all-tokens tokenize)])
    (println tok))
  (define module-datum `(module fpy-mod "fpy-tokenize.rkt"
                          '()))
  (datum->syntax #f module-datum)
)

(define (all-tokens tokenizer)
  ; run a tokenizer until #<eof> is found and return all found tokens
  (define (all-tokens-accum accum)
    (define token (tokenizer))
    (if (equal? (str token) "#<eof>")
        (reverse accum)
        (begin
          #;(println (str token))
         (all-tokens-accum (cons token accum)))))
  (all-tokens-accum '()))

(define (make-tokenizer port)
  (port-count-lines! port)
  (define (next-token)
    (fpy-lexer port))
  next-token)

(define (all-tokens/string a-string)
  (define my-port
    (open-input-string a-string))
  (define my-tokenize (make-tokenizer my-port))
  (all-tokens my-tokenize))

(define-syntax (fpy-module-begin HANDLE-EXPR)
  #'(#%module-begin
     HANDLE-EXPR))

(provide (rename-out [fpy-module-begin #%module-begin]))

#;(all-tokens/string "x:Int")