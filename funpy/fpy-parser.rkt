#lang brag

module: imports (block|function_def)*

imports: (module-import|from-import|NEWLINE)*

import_stmt: import_name | import_from

import_name: 'import' dotted_as_names 

import_from:
    | 'from' ('.' | '...')* dotted_name 'import' import_from_targets 
    | 'from' ('.' | '...')+ 'import' import_from_targets 

import_from_targets:
    | '(' import_from_as_names [','] ')' 
    | import_from_as_names !','
    | '*'

import_from_as_names:
    | ','.import_from_as_name+ 
import_from_as_name:
    | NAME ['as' NAME ] 
dotted_as_names:
    | ','.dotted_as_name+ 
dotted_as_name:
    | dotted_name ['as' NAME ] 
dotted_name:
    | dotted_name '.' NAME 
    | NAME

module-import: "import" import-path ("as" ID)? NEWLINE
# import-path: NAME ("." NAME)*

dotted_name:
    | dotted_name '.' NAME 
    | NAME

# Python diff: we use expressions here instead of named_expressions...
if_expr:
      'if' expression ':' block elif_expr
    | 'if' expression ':' block [else_expr] 
elif_expr:
      'elif' expression ':' block elif_expr
    | 'elif' expression ':' block [else_expr] 
else_expr:
      'else' ':' (block | expression)

simple_stmt:
      assignment
    # | star_expressions 
    # | return_stmt
    # | import_stmt
    # | raise_stmt
    # | 'pass'   # Just use none as an expression  
    # | del_stmt
    # | yield_stmt
    | assert_stmt
    # | 'break' 
    # | 'continue' 
    # | global_stmt  TODO
    # | nonlocal_stmt  TODO: ?

compound_stmt:
      function_def
    | if_expr
    # | struct_def # TODO
    # | with_stmt
    | for_expr
    # | try_expression  # Maybe no exceptions??
    # | while_expression # TODO
    # | match_expression


assignment: ID "=" expression

assert_stmt: 'assert' expression [',' expression ]

for_expr:
    'for' targets 'in' ~ star_expressions ':' block [else_expr] 
    # | ASYNC 'for' targets 'in' ~ star_expressions ':' [TYPE_COMMENT] block [else_block] 


# fun-apply: expression "(" (pos-arg ("," pos-arg)*)? (kw-arg ("," kw-arg))? ")"
# pos-arg: expression
# kw-arg: ID "=" expression 
block: "⟦" NEWLINE? (simple_stmt NEWLINE)* "⟧"

function_def:
    # | decorators function_def_raw 
    function_def_raw

function_def_raw: 'def' ID '(' [parameters] ')' [':' type-expr ] '=' block
parameters:
      slash_no_default param_no_default* param_with_default* [star_etc] 
    | slash_with_default param_with_default* [star_etc] 
    | param_no_default+ param_with_default* [star_etc] 
    | param_with_default+ [star_etc] 
    | star_etc

slash_no_default:
      param_no_default+ '/' ',' 
    | param_no_default+ '/' &')' 

slash_with_default:
      param_no_default* param_with_default+ '/' ',' 
    | param_no_default* param_with_default+ '/' &')' 

param_no_default:
      param ','
    #| param &')'
     | param 

param_with_default:
    param default ','
    | param default &')'

param_maybe_default:
      param default? ','
    | param default?  &')' 

param: NAME annotation?

default: '=' expression

annotation: ':' type-expr 

star_etc: '*' param_no_default param_maybe_default* [kwds] 
    | '*' ',' param_maybe_default+ [kwds] 
    | kwds

kwds: '**' param_no_default 

fun-name: NAME
# fun-args: fun-arg (, fun-arg)*
return-type-spec: ":" type-expr "="
type-expr: TYPE-NAME
# | type-apply
# type-apply: TYPE-ID "[" type-expr ("," type-expr )* "]"

expressions:
      expression (',' expression )+ [','] 
    | expression ',' 
    | expression

expression:
      disjunction 'if' disjunction 'else' expression 
    | disjunction
    # | lambdef  # v0.2

disjunction:
      conjunction ('or' conjunction )+ 
    | conjunction

conjunction:
      negation ('and' negation )+ 
    | negation

negation:
      'not' negation 
    | comparison

comparison:
      bitwise_or compare_op_bitwise_or_pair+ 
    | bitwise_or
compare_op_bitwise_or_pair:
      eq_bitwise_or
    | noteq_bitwise_or
    | lte_bitwise_or
    | lt_bitwise_or
    | gte_bitwise_or
    | gt_bitwise_or
    | notin_bitwise_or
    | in_bitwise_or
    | isnot_bitwise_or
    | is_bitwise_or
eq_bitwise_or: '==' bitwise_or 
noteq_bitwise_or:
      ('!=' ) bitwise_or 
lte_bitwise_or: '<=' bitwise_or 
lt_bitwise_or: '<' bitwise_or 
gte_bitwise_or: '>=' bitwise_or 
gt_bitwise_or: '>' bitwise_or 
notin_bitwise_or: 'not' 'in' bitwise_or 
in_bitwise_or: 'in' bitwise_or 
isnot_bitwise_or: 'is' 'not' bitwise_or 
is_bitwise_or: 'is' bitwise_or 

bitwise_or:
      bitwise_or '|' bitwise_xor 
    | bitwise_xor
bitwise_xor:
      bitwise_xor '^' bitwise_and 
    | bitwise_and
bitwise_and:
      bitwise_and '&' shift_expr 
    | shift_expr
shift_expr:
      shift_expr '<<' sum 
    | shift_expr '>>' sum 
    | sum

sum:
      sum '+' term 
    | sum '-' term 
    | term


term:
      term '*' factor 
    | term '/' factor 
    | term '//' factor 
    | term '%' factor 
    | term '@' factor 
    | factor
factor:
      '+' factor 
    | '-' factor 
    | '~' factor 
    | power

power:
      await_primary '**' factor 
    | await_primary

await_primary:
    # | AWAIT primary   # v0.3
      primary

primary:
      primary '.' NAME 
    | primary '(' [arguments] ')' 
    | primary '[' slices ']' 
    | atom
    # | primary genexp  # TODO ?
    
slices:
      slice !',' 
    | slice (',' slice)* [','] 
slice:
    [expression] ':' [expression] [':' [expression] ] 
    # | named_expression

atom:
      NAME
    | 'true' 
    | 'false'
    | 'none' 
    | strings
    | INTEGER
    | NUMBER
    # | (tuple | group | genexp)   Python 3.10
    | (tuple | genexp)
    | (list | listcomp)
    | (dict | set | dictcomp | setcomp)
    | '...'

strings: STRING+ kwarg_or_starred

arguments: args [','] &')' 
args:
      ','.(starred_expression | (expression !':=') !'=')+ [',' kwargs ] 
    | kwargs

kwargs:
      kwarg_or_starred (',' kwarg_or_starred)* ','
      kwarg_or_double_starred (',' kwarg_or_double_starred)* 
    | kwarg_or_starred (',' kwarg_or_starred)* ','
    | kwarg_or_double_starred (',' kwarg_or_double_starred)*
starred_expression:
      '*' expression 
kwarg_or_starred:
      NAME '=' expression 
    | starred_expression 
kwarg_or_double_starred:
      NAME '=' expression 
    | '**' expression 

tuple: '(' [star_expression ',' [star_expressions]  ] ')' 
genexp: '(' ( expression !':=') for_if_clauses ')' 

set: '{' star_expressions '}'
setcomp: '{' expression for_if_clauses '}'

dict: '{' [double_starred_kvpairs] '}'
dictcomp: '{' kvpair for_if_clauses '}'

list:'[' [star_expressions] ']' 
listcomp: '[' expression for_if_clauses ']'

star_expressions: star_expression (',' star_expression)* [','] 
star_expression:
     '*' bitwise_or 
    | expression

double_starred_kvpairs:  double_starred_kvpair (',' double_starred_kvpair)* [','] 
double_starred_kvpair:
      '**' bitwise_or 
    | kvpair

kvpair: expression ':' expression 

for_if_clauses: for_if_clause+

for_if_clause:
    # ASYNC 'for' star_targets 'in' ~ disjunction ('if' disjunction )* 
    'for' targets 'in' ~ disjunction ('if' disjunction )* 


# assignment_expression:
#     | NAME ':=' ~ expression

# DIFF with Python: simplify target -> targets dropping
# star cases
# TODO: handle 
targets:
      target !','
    | target (',' target)* [',']

targets_list_seq: target (',' target)* [','] 

targets_tuple_seq:
      target (',' target )+ [','] 
    | target ',' 

target:
      t_primary '.' NAME ! t_lookahead 
    | t_primary '[' slices ']' ! t_lookahead 
    # | star_atom

# start_atom:
#      NAME 
#    | '(' target ')' 
#    | '(' [targets_tuple_seq] ')' 
#    | '[' [targets_list_seq] ']' 

single_target:
      single_subscript_attribute_target
    | NAME 
    | '(' single_target ')' 

single_subscript_attribute_target:
      t_primary '.' NAME ! t_lookahead 
    | t_primary '[' slices ']' ! t_lookahead 

t_primary:
      t_primary '.' NAME & t_lookahead 
    | t_primary '[' slices ']' & t_lookahead 
    | t_primary genexp & t_lookahead 
    | t_primary '(' [arguments] ')' & t_lookahead 
    | atom & t_lookahead 

t_lookahead: '(' | '[' | '.'

