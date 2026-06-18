
{ SinOsc.ar(300 + LFTri.kr(2, mul:30), 0, 0.2) }.play;

{  LFTri.kr(10).linexp( -1.0, 1.0, 0.01, 1.0) }.plot(0.1);


{ SinOsc.ar(300 + LFTri.kr(2).linexp(-1.0, 1.0, 1, 100.0), 0, 0.2) }.scope;

