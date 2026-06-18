// https://doc.sccode.org/Browse.html#Tutorials%3EGetting-Started

// 'Posting' text
(
"Hello World!".postln;
)

// 04. Functions and other

{ [SinOsc.ar(440, 0, 0.2), SinOsc.ar(442, 0, 0.2)] }.play;
// Array of two synths, one for each channel.


// Declare a function (but don't run it):
f = { "asdad".postln };

// Actually evaluate (call) it
f.value;


// Fun with arguments
(
f = { arg a, b;
	a - b;
};
f.value(5, 3); // works
// f.value("asda", 3)
// Error: Messaage '-' not understood
// What's happening? string doesn't understand message '-'
)

// Fun with keyword arguments
(
f = { arg a, b;
	a - b;
};
f.value(5, b:3);  // regular (positional) args should come before keyword args!
)


(
	f = {
		5 + 3 * 2
	};
	f.value;
) // prints 16 = (5 + 3) * 2

// GOTCHA! No operator precedence, operators are applied left to right, unless parenthesis are used

// Alternate arg declaration: |a, b| instead of arg a, b:
(
   g = { |a, b|
	  a + b
   };
   g.value(3, 4);
)


// 05. Functions and sound

{ SinOsc.ar(440, 1.0, 0.2) }.play;


// SinOsc.kr modulating amplitude of SinOsc.ar
(
{ var ampOsc;
    // ampOsc = SinOsc.kr(0.5, 1.5pi, 0.5, 0.5);
	ampOsc = SinOsc.kr(70, 1.5pi, 0.5, 0.5);
	// ampOsc = SinOsc.kr(7, 1.5pi, 0.5, 0.5);
    SinOsc.ar(440, 0, ampOsc);
}.play;
)


// Multichannel expansion:
{ SinOsc.ar([440, 442], 0, 0.2) }.play;
// this is equivalent to:
{ [SinOsc.ar(440, 0, 0.2), SinOsc.ar(442, 0, 0.2)] }.play;


// Randomness for picking the parameters
(
{ var freq;
    freq = [[660, 880], [440, 660], 1320, 880].choose;
    SinOsc.ar(freq, 0, 0.2);
}.play;
)

// Panning between channels:
// Pan2 :
//  1. first argument is sound signal,
//  2. second argument controls wether sound goes to left (-1) or right (+1)
{ Pan2.ar(PinkNoise.ar(0.2), SinOsc.kr(0.5)) }.play;


// 07. Mix it up
{ PinkNoise.ar(0.2) + SinOsc.ar(440, 0, 0.2) + Saw.ar(660, 0.2) }.play;

{ Saw.ar(200, 0.2) }.play;


// one channel
{ Mix.new([SinOsc.ar(440, 0, 0.2), Saw.ar(660, 0.2)]).postln }.play;

{ Mix([SinOsc.ar(440, 0, 0.2), Saw.ar(660, 0.2)]).postln }.play;


{ Saw.ar(442, 2, 0.2)+ Saw.ar(440, 0.2) }.play;

// combine two stereo arrays
(
{
    var a, b;
    a = [SinOsc.ar(440, 0, 0.2), Saw.ar(662, 0.2)];
    b = [SinOsc.ar(442, 0, 0.2), Saw.ar(660, 0.2)];
    Mix([a, b]).postln;
}.play;
)

// Eerie
(¨
    var n = 1;
    //{ Mix.fill(n, { SinOsc.ar(200 + 20.0.rand, 0, 1 / n) }) }.play;
    // { Mix.fill(n, { SinOsc.ar(200 + 200.0.rand, 0, 1 / n) }) }.play;
    { Mix.fill(n, { SinOsc.ar(200 + 500.0.rand, 0, 1 / n) }) }.play;
// { Mix.fill(n, { SinOsc.ar(200 + (200 * ([1, 1.333, 1.5, 1.333 * 1.5, 2.0].choose)), 0, 1 / n)}) }.play

// { Mix.fill(n, { Saw.ar(200 + (200 * ([1, 1.333, 1.5, 1.333 * 1.5, 2.0].choose)),  1 / n)}) }.play;

)

(
// { LFSaw.ar(200, 0, 0.2) - LFSaw.ar(200, 0.5, 0.2) }.scope;
// { LFSaw.ar(200, 0, -0.2) }.scope;
{ LFTri.ar(200, 0, 0.2) + SinOsc.ar(200, phase:0, mul: 0.2) }.scope;

)


// Look at the post window for frequencies and indices
(
    var n = 8;
    {
        Mix.fill(n, { arg index;
            var freq;
            index.postln;
		    // freq = 440 + index;
		    freq = 440 + (index * 0.5);
		    //freq = 440 + (index * 0.3);
            freq.postln;
            SinOsc.ar(freq , 0, 1 / n)
        })
    }.play;
)

(
{ Saw.ar(XLine.kr(40,4000,6),0.2) }.play;
)

(
{
	// PinkNoise.ar(0.2)
	// + BrownNoise.ar(0.2)
	SinOsc.ar(300 + LFTri.kr(2, mul:30), 0, 0.2)
	// Saw.ar(660, 0.2)
	// LFSaw.ar(440)
// }.play
// }.plot;
}.scope(zoom: 20)
)