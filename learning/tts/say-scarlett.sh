#!/bin/bash
"Usage:
$0 "text to say"
"

# acti tts
TRAIN_DIR=/home/teo/data/tts/models/scarlet/glow-tts-scarlet-April-21-2023_07+23PM-1e51a6a

ls -lrt $TRAIN_DIR

tts --model_path $TRAIN_DIR/best_model.pth --config_path $TRAIN_DIR/config.json \
    --text "$1"  --out_path scarlet-says.wav

ffplay scarlet-says.wav
