
#using Pkg
#using DataStructures


⊂ = issubset

function ispangram(input :: String) :: Bool
  counts = Dict{Char, Int64}()
  for ch in lowercase( input )
    counts[ch] = get(counts, ch, 0) + 1
  end

  letters =  Set( keys(counts) )
  # println( "letters: $letters" )

  Set('a':'z') ⊂ letters
end


ispangram("the 1 quick brown fox jumps over the 2 lazy dogs")



function count_nucleotides(strand :: String) :: Dict{Char, Int}
    counts = Dict{Char, Int64}('A' => 0, 'C' => 0, 'T' => 0, 'G' => 0)
    for ch in strand
      if ch ∉ "ACTG"
        throw(DomainError("Bad Nucleotide"))
      end
      counts[ch] = get(counts, ch, 0) + 1
    end

    counts
end

count_nucleotides("GATTACA")


function collatz_steps( n::Int64 ) :: Int64
    steps :: Int64 = 0

    (n >= 1) || throw(DomainError("n is not positive"))

    m :: Int64 = n

    while m != 1
        # println( "steps=$steps m=$m" )

        m = (m % 2 == 0) ? (m / 2) : (3m + 1)
        steps += 1
    end
    return steps
end

collatz_steps(3)


using Base

⊳( obj, fun ) = fun(obj)

struct AB
   x :: Float64
end

a = AB(3)

using Dates

struct Clock
   total_mins :: Int16

   Clock( total_mins :: Int16 ) = new(total_mins)
   Clock(hrs_ :: Int64, mins_ :: Int64) = _make_clock( hrs_, mins_ )
end

MINS_DAY = 24*60 ::Int64

function _make_clock( hrs_::Int64, mins_::Int64 ) :: Clock
    total_mins = (hrs_ * 60 + mins_) % MINS_DAY
    total_mins = (total_mins >= 0 ? total_mins : total_mins + MINS_DAY)
    Clock( convert(Int16, total_mins) )
end

+( c::Clock, m:Dates.Minute ) = Clock( c.total_mins + m.value )



f(obj :: AB) = obj.x + 3

g(obj :: Float64) = println("hello $obj")

a |> f |> g


using Random.Random;

GENERATED_NAMES = Set{String}()

mutable struct Robot
  name :: String
  Robot() = new(_generate_name())
end


function name( r::Robot )
  r.name
end

function reset!( r::Robot )
  r.name = _generate_name()
end


# import Base:+


function _generate_name()
  while true
    name =  Random.randstring( 'A':'Z', 2) * Random.randstring('0': '9', 3)
    if name ∉ GENERATED_NAMES
      push!( GENERATED_NAMES, name )
      return name
    end
  end
end


function luhn(x :: String)
  no_spaces = replace( x, " " => "" )
  n = length(no_spaces)
  evens = [ parse(Int8, x) for x in split(no_spaces[(n-1):-2:1], "" ) ]
  odds  = [ parse(Int8, x) for x in split(no_spaces[n:-2:1], "" ) ]
end

function matching_brackets(x :: String)

  parens:: Set{String} = set(["{", "}", "(", ")", "[", "]"] )
  close_to_open = { "}": "{", "]": "[", ")": "(" }

  stack :: Vector{String} = []


end