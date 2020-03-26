#!/bin/bash

ps -aux | grep "gunic.*$PORT.*avm" | grep -v "grep gunic"  | awk -F ' ' '{print $2 }' | xargs -I {} kill {}
