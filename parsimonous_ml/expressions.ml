open Base

type expr_alt =
  | Literal of string

type expr = {name: string;
             ea: expr_alt;
             identity_tuple: string }


type node = {
  expr: expr;
  full_text: string;
  start: int;
  end_ : int;
  children: node array
}

let rec eq_node (self: node) (other: node) =
    String.(self.full_text = other.full_text)
    && Int.(self.start = other.start)
    && Int.(self.end_ = other.end_)
    && Array.equal (eq_node) self.children other.children

module Node = struct
  type t = node

  let create (expr: expr) (full_text: string) (start: int) (end_: int) : node
    = {expr; full_text; start; end_; children=[||]}

  let expr_name (self: t) = self.expr.name
  let to_seq (self: t): node Sequence.t =
     Array.to_sequence self.children

  let text (self: t): string =
      String.sub self.full_text ~pos:self.start
        ~len:(self.end_ - self.start)

  let (=) (self: t) (other: t) = eq_node self other

  (* let is_in_progress (self: t) =
      match t.node_alt with | InProgress -> true | _ -> false *)
end

type node_w_status =
  | InProgress
  | Done of node


type dict_str_str = string Map.M(String).t

exception ParseError of string
(*
https://github.com/erikrose/parsimonious/blob/master/parsimonious/expressions.py
*)

type object_id = ObjId of int


let obj_id(obj: 'a): object_id = ObjId ( Caml.Obj.magic obj )


module DefaultDict = struct
  type ('a, 'b) t = {
      data: ('a, 'b) Hashtbl.t;
      default: unit -> 'b
  }

  let create ~(default: unit -> 'b) = {
      data= Hashtbl.create(module Int); (*TODO how to make this generic*)
      default=default
  }

  let find (self: ('a, 'b) t) ~(key:'a) : 'b =
    match Hashtbl.find self.data key with
    | Some v -> v
    | None -> (
        Hashtbl.set self.data ~key ~data:(self.default());
        Hashtbl.find_exn self.data key )
end

type parse_cache = (object_id, (int, node_w_status) Hashtbl.t) DefaultDict.t


type parse_state = {
  text: string;
  pos: int;
  error: string;
  cache: parse_cache
}


let starts_with (text: string) ~(prefix: string) ~(pos: int) =
  String.is_substring_at text ~pos: pos ~substring:prefix

module Expression = struct

  (* expression alternatives *)
  type t = expr

  (* let _uncached_match (self: t) (ps: parse_state) : node option =
    match self.ea with
    | Literal lit ->  *)

  let hash (_self: t): int64 = failwith "Unimplemented hash"

  let _uncached_match (self: t) (ps: parse_state): node option =
    match self.ea with
    | Literal lit ->
        if starts_with ps.text ~prefix:lit ~pos:ps.pos then
          Some( Node.create self ps.text ps.pos (ps.pos + String.length lit) )
        else
          None


  let match_core (self:t) (ps: parse_state) =
    (*  Internal guts of ``match()``
        This is appropriate to call only from custom rules or Expression
        subclasses.
        :arg cache: The packrat cache::
            {(oid, pos): Node tree matched by object `oid` at index `pos` ...}
        :arg error: A ParseError instance with ``text`` already filled in but
            otherwise blank. We update the error reporting info on this object
            as we go. (Sticking references on an existing instance is faster
            than allocating a new one for each expression that fails.) We
            return None rather than raising and catching ParseErrors because
            catching is slow.

    *)
    let expr_cache = DefaultDict.find ps.cache ~key:(obj_id(self)) in
    let node_st = match Hashtbl.find expr_cache ps.pos with
      | Some( node_st ) -> node_st
      | None -> (
        (* expr_cache[pos] = IN_PROGRESS  # Mark as in progress *)
          Hashtbl.set expr_cache ~key:ps.pos ~data:InProgress;
          let parsed_node = _uncached_match self ps in
          Hashtbl.set expr_cache ~key:(ps.pos) ~data:parsed_node;
          Hashtbl.find_exn expr_cache ps.pos
      ) in ()

  let match_ (self:t) (ps: parse_state) =
    (* Return the parse tree matching this expression at the given
    position, not necessarily extending all the way to the end of ``text``.
    Raise ``ParseError`` if there is no match there.
    :arg pos: The index at which to start matching
    *)
    let error = ParseError ps.text in
    let node = match_core self

  let parse (self: t) ~(text: string) ~(pos: int) =
      let node_ = match_ self ~text ~pos
end
