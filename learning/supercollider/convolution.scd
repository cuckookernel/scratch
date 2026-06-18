// 1. Allocate a short power-of-two buffer for the impulse response (IR)
~kernelSize = 512;
b = Buffer.alloc(s, ~kernelSize, 1);

// 2. Generate the Gaussian shape (-3.0 to 3.0 captures the clean decay)
~gaussian = Signal.newClear(~kernelSize).waveFill({ |x| x.pow(2).neg.exp }, -3.0, 3.0);

// 3. Load it onto the server
b.loadCollection(~gaussian);


~gaussian.plot;


s.initTree;

(
{
    var trigger, grains, grains0;

    // A stream of random impulses (density of 30 spikes per second)
    trigger = Dust.ar(3, mul: 0.000001);

    // Convolve the raw impulses with our Gaussian buffer
    // 'framesize' must match or exceed the buffer size
    grains0 = Convolution.ar(trigger, b, framesize: ~kernelSize);

    // Multiply by a high frequency oscillator to turn the windows into audible tones
    grains = grains0 * SinOsc.ar(200);

    // Pan2.ar(grains * 0.5, 0);
	grains
// }.play;
// }.plot(1.0);
	}.scope
)


(
{
    var trigger, density, totalGrains;

    density = LFNoise1.kr(1).linexp(-1, 1, 10, 150); // Modulate density over time
    trigger = Dust.ar(density);

    totalGrains = TGrains.ar(
        numChannels: 2,
        trigger: trigger,
        bufnum: b, // Reads our pre-allocated Gaussian buffer!
        rate: 1.0, // Normal playback speed
        centerPos: ~kernelSize / (2 * SampleRate.ir), // Point to the center of the buffer
        dur: 0.02, // Grain duration (20 milliseconds)
        pan: TRand.ar(-0.8, 0.8, trigger), // Instantly randomize the stereo field per grain
        amp: TRand.ar(0.1, 0.5, trigger)  // Instantly randomize the volume per grain
    );

    // Multiply by an internal carrier texture to hear the grain cloud definition
    totalGrains * LFSaw.ar(120, mul: 0.2);
}.play;
)