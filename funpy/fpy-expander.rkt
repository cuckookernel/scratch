#lang br/quicklang
(require "fpy-parser.rkt")
(require "fpy-lexer.rkt")

(provide read-syntax parse program make-tokenizer quote)

(define (read-syntax path port)
  (define parse-tree (parse path (make-tokenizer port)))
  (define module-datum `(module bf-mod "fpy-reader.rkt"
                          ,parse-tree))
  (datum->syntax #f module-datum)
)

(define (make-tokenizer port)
  (port-count-lines! port)
  (define (next-token)
    (fpy-lexer port))
  next-token)

(define-macro (fpy-module-begin HANDLE-EXPR ...)
  #'(#%module-begin
     HANDLE-EXPR ...))

(define (program a)
  (display a))

(provide (rename-out [fpy-module-begin #%module-begin]))
