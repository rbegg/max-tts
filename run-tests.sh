#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "TTS_VOICE = " $TTS_VOICE

/run.sh --voice $TTS_VOICE &

sleep 3

export PATH="/opt/venv/bin:$PATH"

echo "Started Server, ready for testing!"

sleep infinity