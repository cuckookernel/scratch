
wpctl status

# 1. Start audio synth server under PipeWire (pw)

```bash
pw-jack scsynth -u 57110   # -u is for UDP
```

Expected output:
```
Found 0 LADSPA plugins
JackDriver: client name is 'SuperCollider'
SC_AudioDriver: sample rate = 48000.000000, driver's block size = 1024
SuperCollider 3 server ready.
Zeroconf: registered service 'SuperCollider'
FAILURE IN SERVER /s_new Group 1 not found
```


## 2. Wire supercollider outputs to particular audio devices:


### For analog audio-jack


```bash
pw-link SuperCollider:out_1 alsa_output.pci-0000_80_1f.3.analog-stereo:playback_FL  # Left channel
pw-link SuperCollider:out_2 alsa_output.pci-0000_80_1f.3.analog-stereo:playback_FR  # Right channel
```

### For bluetooth speakers (click due to drop outs)

```bash
pw-link  SuperCollider:out_1 bluez_output.80_99_E7_2C_C7_D6.1:playback_FL  # Left channel
pw-ling  SuperCollider:out_2 bluez_output.80_99_E7_2C_C7_D6.1:playback_FR  # Right channel
```

## 3. Run sclang script on scide


Run with `Ctrl+Enter`  on each block:

```c
(
s.startAliveThread;
s.meter;
)

s.initTree; // this is key!

{ SinOsc.ar(440, 0, 0.2) ! 2 }.play;
```


`Ctrl+.` to silence