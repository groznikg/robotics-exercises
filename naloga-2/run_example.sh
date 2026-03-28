#!/bin/bash
# Example run: A=(0,0), B=(3,4) → 500 km diagonal
# Initial heading 53° (roughly toward B), sample wind file
python3 simulate.py 0 0 3 4 53 wind.txt
