#lang br/quicklang
(define (read-syntax path port)
  (define src-lines
    (port->lines port))
  (define src-datums
    (format-datums '~a src-lines))
  (define module-datums
     `(module stacker-mod "stacker.rkt"
        (handle-args ,@src-datums)))
  (datum->syntax #f module-datums)
)

(provide read-syntax)

(define-macro (stacker-module-begin HANDLE-EXPR)
  #'(#%module-begin
     (display (first HANDLE-EXPR))))

(provide (rename-out [stacker-module-begin #%module-begin]))


(define (push-stack stack arg)
  (cons arg stack))

(define (handle stack [arg #f])
  (cond
    [(number? arg) (push-stack stack arg)]
    [(or (equal? * arg) (equal? + arg))
     (define op-result (arg (first stack) (second stack)))
     (push-stack stack op-result)]))

(define (handle-args . args)
  (for/fold ([stack-acc empty])
            ([arg (in-list args)]
            #:unless (void? arg))
    (handle stack-acc arg)
  ))


(provide handle-args + *)
 
