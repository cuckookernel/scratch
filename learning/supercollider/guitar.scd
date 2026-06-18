// Guitar string simulation
(
{
    var trigger, excitation, pitch, delayTime, string;

    // 1. The Pick (Trigger)
    // Fires a pluck 2 times a second
    // trigger = Impulse.ar(2);
	trigger = Impulse.ar(10);

    // 2. The Pitch Calculation
    // Choose a random MIDI note between 40 (Low E string) and 64 (Middle E)
    // pitch = TRand.ar(40, 64, trigger).round(1);
	pitch = TRand.ar(20, 50, trigger).round(1);
    delayTime = pitch.midicps.reciprocal; // Convert frequency to period time (1/f)

    // 3. The Noise Burst (Excitation)
    // A tiny 10-millisecond burst of white noise when the trigger fires.
    // This simulates the actual scrape of the plectrum.
    excitation = PinkNoise.ar(0.5) * EnvGen.ar(Env.perc(0.001, 0.01), trigger);

    // 4. The String Simulator (The UGen Engine)
    string = Pluck.ar(
        in: excitation,          // The noise burst to feed into the delay line
        trig: trigger,           // Re-instantiates the string loop
        maxdelaytime: 0.2,       // Maximum buffer allocation slot
        delaytime: delayTime,    // Current string length (tuning)
        decaytime: 6,            // How many seconds the string rings out
        //coef: 0.1               // Damping factor (0 = no damping, 0.9 = dull nylon string)
		coef: 0.9               // Damping factor (0 = no damping, 0.9 = dull nylon string)
    );

	// Critical params
	// decaytime: This controls how long the feedback loop sustains.
	//   A long decay time simulates a steel string on an electric guitar;
	//   a short decay time simulates a muted string or a banjo.
	// coef (The Loss Filter):
	// This coefficient dictates the internal low-pass blending ratio.
	/// Every time the audio block loops around, the current sample is averaged with the previous sample:
	// If you set coef close to 0.0, the filter is wide open, keeping the harmonics bright, metallic,
	// and sharp. If you push coef toward 0.5 or higher, the high frequencies drop out instantly,
	// shifting the timbre into a warm, dark, nylon-string jazz classical guitar or a pizzicato violin pluck.

    // 5. Spatialization & Body Resonance
    // Pass it through a gentle low shelf filter to mimic a wooden guitar body
    string = BLowShelf.ar(string, freq: 200, db: 3);

    Pan2.ar(string, pos: -1);
}.play;
)

(
s.startAliveThread;
s.meter;
)

s.initTree;


(
var guitar_sim;
var tempo = 10;
var trigger = Impulse.ar(tempo);
var pitch = TRand.ar(20, 50, trigger).round(1);
var delaytime = pitch.midicps.reciprocal; // Convert frequency to period time (1/f)

guitar_sim = { |trigger, delaytime, coef, decaytime|
	// Example:
	// tempo = 10
	// trigger = Impulse.ar(tempo);
	// pitch = TRand.ar(20, 50, trigger).round(1);
	// delayTime = pitch.midicps.reciprocal; // Convert frequency to period time (1/f)

	var excitation, string;

	excitation = PinkNoise.ar(0.5) * EnvGen.ar(Env.perc(0.001, 0.01), trigger);

    string = Pluck.ar(
        in: excitation,         // The noise burst to feed into the delay line
        trig: trigger,          // Re-instantiates the string loop
        maxdelaytime: 0.2,      // Maximum buffer allocation slot
        delaytime: delaytime,   // Current string length (tuning)
        decaytime: decaytime,   // How many seconds the string rings out
        coef: coef              // Damping factor (0 = no damping, 0.9 = dull nylon string)
    );

	string = BLowShelf.ar(string, freq: 200, db: 3);

    Pan2.ar(string, pos: -1);

};

{guitar_sim.value(trigger:trigger, delaytime:delaytime, coef:0.9, decaytime:6)}.play;

)