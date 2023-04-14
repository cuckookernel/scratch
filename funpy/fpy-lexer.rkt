#lang racket
(require brag/support)

(define-lex-abbrev digits (:+ (char-set "0123456789")))

(define-lex-abbrev type-name-first
  (char-range #\A #\Z) )

(define-lex-abbrev name-fst
  (:or #\_ (char-range #\a #\z) (char-range #\A #\Z) ))

(define-lex-abbrev name-rest
  (:or name-fst (char-range #\0 #\9) #\!))


(define fpy-lexer
  (lexer
   ["\n" (token 'NEWLINE lexeme)]
   [whitespace (token lexeme #:skip? #t)]
   ; [(from/stop-before "rem" "\n") (token 'REM lexeme)]
   [(:or "def"  "from" "import" "as" "for" "not" "in" "=="
         "is" "none" "true" "false" "<=" ">=" "==" "!=" "**"
         (char-set "⟦⟧{}+:=(),."))
    (token lexeme lexeme)]
   [digits (token 'INTEGER (string->number lexeme))]
   [(:or (:seq (:? digits) "." digits)
         (:seq digits "."))
    (token 'DECIMAL (string->number lexeme))]
   [(:seq type-name-first (:* name-rest))
    (token 'TYPE-NAME lexeme)]
   [(:seq name-fst (:* name-rest))
    (token 'NAME lexeme)]
   [(:or (from/to "\"" "\"") (from/to "'" "'"))
    (token 'STRING
           (substring lexeme
                      1 (sub1 (string-length lexeme))))]))

(provide fpy-lexer)