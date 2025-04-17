#!/bin/bash

XVFB_DISPLAY=:99
Xvfb $XVFB_DISPLAY -screen 0 1920x1080x16 &

export DISPLAY=$XVFB_DISPLAY

# Run script with all CLI args
python fuck-udemy.py "$@"
