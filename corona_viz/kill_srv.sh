#!/bin/bash

ps -aux | grep "gunic.*corona" | grep -v "grep gunic"  | awk -F ' ' '{print $2 }' | xargs -I {} kill {}
