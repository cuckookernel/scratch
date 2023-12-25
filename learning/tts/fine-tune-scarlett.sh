#!/bin/bash
TTS_GIT_REPO=/home/teo/git/_third_party/coqui-tts/
CUDA_VISIBLE_DEVICES="0" python $TTS_GIT_REPO/TTS/bin/train_tts.py \
  --config_path ./config-scarlett-glow.json \
  --restore_path ~/.local/share/tts/tts_models--en--ljspeech--glow-tts/model_file.pth
