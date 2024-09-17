#!/bin/bash
"Usage:
$0 "text to say"
"

# acti tts
TRAIN_DIR=/home/teo/data/tts/models/scarlett/glow-tts-scarlett-April-21-2023_08+14PM-1e51a6a

ls -lrt $TRAIN_DIR

for file in  $(ls -1 $TRAIN_DIR/checkpoint_*); do
  echo "$file"

  out_file=scarlet-says-$(basename $file).wav


  CUDA_VISIBLE_DEVICES="0" tts --model_path $file \
      --config_path $TRAIN_DIR/config.json \
      --text "$1"  --out_path $out_file
  # ffplay $out_file -autoexit

done