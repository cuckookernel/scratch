#lang racket

(struct verb (aliases Desc transitive?))
(struct thing (name [state #:mutable] actions))
(struct place (desc [things #:mutable] actions))


(define names (make-hash))
(define elements (make-hash))

(define (record-element! name val)
  (hash-set! names name val)
  (hash-set! elements val name))

(define (name->element name) (hash-ref names name))

(define south (verb (list 'south 's) "go south" #false))

(define flower (thing "flower1" #f '()))
(record-element! 'flower flower)

(define meadow0 (place "You're in a meadow"
                      (list flower)
                      (list (cons south (lambda () desert) )
                      )))

(define-syntax-rule
  (define-place id desc [thng ...] ([vrb expr] ...))
  (begin
    (define id (place desc
                      (list thng ...)
                      (list (cons vrb (lambda () expr)) ...)))
    (record-element! 'id id)                 
  )
)

(define-place meadow
  "You're in a meadow."
  [flower]
  ([south desert]))


(define-values (a b) (values 3 ))

(define-syntax-rule (define-thing id
                      [vrb expr] ...)
  (begin
    (define id
      (thing 'id #false (list (cons vrb (lambda ())) ...)))
    (record-thing! 'id id)))



(define-thing cactus [pick "auch"])


(define-place desert
  "You're in a desert."
  [cactus key]
  ([north meadow]
   [south desert]
   [east desert]
   [west desert]))
