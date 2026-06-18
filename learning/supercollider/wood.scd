s.initTree;

(
{
    var trigger, impact, wood;

    // 1. The Controller: Irregular, organic knock intervals
    trigger = Dust.ar(3);

    // 2. The Impact (Excitation): Knuckle skin texture
    // A tiny, 4-millisecond burst of Pink Noise combined with the raw trigger spike
    impact = PinkNoise.ar(0.5) * EnvGen.ar(Env.perc(0.001, 0.004), trigger);
    impact = impact + (trigger * 0.5); // Add a hard spike for the core impact structural snap

    // 3. The Wood Body (Resonator Bank)
    wood = Klank.ar(
        `[
            // [175, 285, 410, 630],     // Earthy, low-mid inharmonic resonant modes
			[110, 150, 190, 290],    // hollow door
            [1.0, 0.6, 0.3, 0.15],    // Amplitudes: higher frequencies are much quieter
            [0.20, 0.14, 0.06, 0.024] // Decay times (seconds): High modes die instantly!
        ],
        input: impact
    );

    // 4. Subtle Saturation
    // Real wood compresses slightly under a hard strike; .tanh mimics this physically
    wood = wood.tanh;

    Pan2.ar(wood * 2, 0);
}.play;
)


(
{
    var trigger, impact, wood;

    // 1. The Controller: Irregular, organic knock intervals
	trigger = Dust.ar(50);

    // 2. The Impact (Excitation): Knuckle skin texture
    // A tiny, 4-millisecond burst of Pink Noise combined with the raw trigger spike
    impact = PinkNoise.ar(0.5) * EnvGen.ar(Env.perc(0.001, 0.004), trigger);
    impact = impact + (trigger * 0.5); // Add a hard spike for the core impact structural snap

    // 3. The Wood Body (Resonator Bank)
    wood = Klank.ar(
        `[
            // [175, 285, 410, 630],     // Earthy, low-mid inharmonic resonant modes
			[600, 950, 1300],
            [1.0, 0.6, 0.3],    // Amplitudes: higher frequencies are much quieter
            [0.03, 0.02, 0.01] // Decay times (seconds): High modes die instantly!
        ],
        input: impact
    );

    // 4. Subtle Saturation
    // Real wood compresses slightly under a hard strike; .tanh mimics this physically
    wood = wood.tanh;

    Pan2.ar(wood * 2, 0);
}.play;
)



{ Dust.ar(10) }.plot(2.0);

{ XLine.kr(20000, 2, 10) }.plot(2.0)

{ Dust.ar(XLine.kr(20000, 2, 10), 0.2) }.play;

