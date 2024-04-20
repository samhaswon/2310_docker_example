#!/usr/bin/env ash

# This shell should exit on error
set -e
# Start the server, replacing the current shell process with the server process
exec waitress-serve --port=5000 --call "main:create_app"