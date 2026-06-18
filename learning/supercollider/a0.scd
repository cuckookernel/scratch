Server.killAll;
(
s.startAliveThread;
s.meter;
)

s.initTree;

a = { SinOsc.ar(1200, 0, 0.2) ! 2 }.play;
//{ SinOsc.ar(441, 0, 0.2) ! 2 }.play;
//{ SinOsc.ar(442, 0, 0.2) ! 2 }.play;

(
{
    // 5 harmonically related frequencies, slightly randomized over time
    // var frequencies = [110, 220, 330, 440, 550] * LFNoise1.kr(0.05).range(0.99, 1.01);
	var frequencies = [ 330, 440 ]* LFNoise1.kr(0.05).range(0.90, 1.10);
    var oscillators = SinOsc.ar(frequencies);

    // A filter that cuts off the high end, sweeping up and down rhythmically
    var filter = LPF.ar(oscillators, LFNoise1.kr(0.2).exprange(200, 2000));

    // Splay spreads the mono signals across the stereo field safely
    Splay.ar(filter) * 0.2;
}.play;
)


(
{
    var trigger = Dust.kr(8); // Generates roughly 8 random clicks per second
    var pitch = TRand.kr(100, 200, trigger).round(50); // Picks a random musical pitch on each click
    var env = Decay2.kr(trigger, 0.005, 0.1); // Creates a sharp attack and quick decay envelope

	// Blip.ar(pitch);
    // Blip is an oscillator rich in harmonics
    var sig = Blip.ar(pitch, LFNoise1.kr(1).range(1, 10)) * env;
	// sig;
	//env;
	// Pass it through a feedback delay for that space-echo effect
    CombN.ar(sig, 0.5, [0.25, 0.35], 3) * 0.4;
}.play;
)