#!/bin/bash
# Deck-Tools GUI Launcher for macOS
# Double-click this file to launch the GUI

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to that directory
cd "$DIR"

# Launch the GUI
python3 deck_tools_gui.py
