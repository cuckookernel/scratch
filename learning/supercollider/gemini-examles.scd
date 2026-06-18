Server.killAll;
(
s.startAliveThread;
s.meter;
)

s.initTree;

variable s1;
let s1 = { SinOsc.ar([400, 401], 0, 0.1) * Saw.ar([11, 33], 1) * EnvGen.kr(Env.sine(10)) }

Saw.ar([11, 33],1).plot;

{ Saw.ar([11, 33], 1) * EnvGen.kr(Env.sine(10)) }.play

{ Saw.ar([11, 33], 1) }.play

(
{
    RLPF.ar(
        // in: Saw.ar([100, 102], 0.15),
		in: Saw.ar([100, 120], 0.15),
        freq: Lag.kr(LFNoise0.kr(4, 700, 1100), 0.1),
        rq: 0.05
    )
}.play
)

{ SinOsc.ar([400, 401], 0, 0.5) * Saw.ar([11, 33], 0.5) }.play

s.scope(2)

a = { (SinOsc.ar(200, 0, 0.2) + SinOsc.ar(210, 0, 0.2)) * 0.2 ! 2 }.play;
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


(
{
    // An LFO that controls how fast the siren pitch wobbles
    var lfoSpeed = LFNoise1.kr(0.5).range(1, 8);
    var pitchWobble = SinOsc.kr(lfoSpeed).range(200, 800);

    // The core raw audio wave
    var audio = LFSaw.ar(pitchWobble);

    // A resonant bandpass filter to make it sound hollow and ghostly
    var filter = Resonz.ar(audio, LFNoise1.kr(1).exprange(400, 3000), 0.2);

    // Slowly sweep the sound back and forth between Left and Right channels
    var autoPan = SinOsc.kr(0.3);

    Pan2.ar(filter * 0.2, autoPan);
}.play;
)



(
{
    var numOscs = 4;
    // An A9-sus chord translated from MIDI notes to frequencies (Hz)
    var freqs = [57, 64, 66, 71].midicps;
    var sig;

    // 'collect' loops through our frequencies and creates a layer for each
    sig = freqs.collect({ |f, i|
        // 1. Ultra-slow volume swells unique to each oscillator
        var volumeSwell = LFNoise1.kr(0.03 + (i * 0.01)).range(0.01, 0.12);

        // 2. Micro-detuning to make the sound thick and lush
        var detune = LFNoise1.kr(0.2).range(0.995, 1.005);

        // 3. A variable saw wave where the shape morphs over time
        var osc = VarSaw.ar(f * detune, width: LFNoise1.kr(0.1).range(0.2, 0.8));

        // 4. Send each layer wandering slowly back and forth across the stereo field
        Pan2.ar(osc * volumeSwell, LFNoise1.kr(0.04 + (i * 0.02)));
    }).sum; // Combine all 4 layers together

    // 5. THE MAGIC SAUCE: A massive virtual space wash
    // FreeVerb2 handles stereo input: (Left, Right, mix, roomSize, damping)
    sig = FreeVerb2.ar(sig[0], sig[1], mix: 0.7, room: 0.98, damp: 0.4);

    sig;
}.play;
)

(
{
    var noise = PinkNoise.ar(0.8);

    // Two independent LFOs sweeping through frequencies exponentially (musically)
    var sweepLeft = LFNoise1.kr(0.04).exprange(60, 1000);
    var sweepRight = LFNoise1.kr(0.03).exprange(100, 1500);

    // BPF is a Bandpass Filter. 'rq' is reciprocal of Q.
    // The lower the rq, the narrower and more bell-like the filter sounds.
    var filterLeft = BPF.ar(noise, sweepLeft, rq: 0.005);
    var filterRight = BPF.ar(noise, sweepRight, rq: 0.002);

    // Give each channel its own independent volume pulse
    var leftChan = filterLeft * LFNoise1.kr(0.08).range(0.2, 0.8);
    var rightChan = filterRight * LFNoise1.kr(0.06).range(0.2, 0.8);

    var stereoSig = [leftChan, rightChan];

    // Pass it through a feedback delay that echoes at different rates in each ear
    // CombC: (input, maxDelayTime, currentDelayTime, decayTime)
    stereoSig = stereoSig + CombC.ar(stereoSig, 1.0, [0.55, 0.73], 8);

    // Final volume check to protect your ears
    stereoSig * 0.25;
}.play;
)



(
{
    // 1. Raw pink noise source
    // var noise = PinkNoise.ar(0.8);
	// var noise = BrownNoise.ar(0.8);
	// var noise = WhiteNoise.ar(4.0);

    // 2. FIXED: Safely scale from 0-1 into our exponential frequency range
    // Sped up from 0.04 to 0.15 so you hear the movement right away
    var sweepLeft = LFNoise1.kr(0.15).range(0, 1).exprange(150, 1200);
    var sweepRight = LFNoise1.kr(0.12).range(0, 1).exprange(200, 1600);

    // 3. FIXED: Widened 'rq' (0.04 instead of 0.003) so it's beautifully audible
    var filterLeft = BPF.ar(noise, sweepLeft, rq: 0.04);
    var filterRight = BPF.ar(noise, sweepRight, rq: 0.03);

    // 4. Smooth volume pulses for both ears
    var leftChan = filterLeft * LFNoise1.kr(0.2).range(0.3, 0.9);
    var rightChan = filterRight * LFNoise1.kr(0.15).range(0.3, 0.9);

    var stereoSig = [leftChan, rightChan];

    // 5. Deep space feedback delay
    stereoSig = stereoSig + CombC.ar(stereoSig, 1.0, [0.35, 0.53], 6);

    // Boosted final master volume multiplier to 0.4
    stereoSig * 2.0;
	//noise;
	//filterLeft;
}.play;
)

{ LFNoise1.ar(500, 0.25) }.play;


(
SynthDef("help-LFClipNoise", { |out = 0|
    Out.ar(out,
        LFClipNoise.ar(1000, 0.25)
    )
}).play;
)


