#!/bin/bash

docker build ./ -t nine_box
docker run -p5006:5006 nine_box

echo "Point browser to: http://localhost:5006/nine_box"
