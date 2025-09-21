#!/bin/bash

# Build Phase 3 C Frontend

set -e

echo "Installing dependencies..."
sudo apt-get update
sudo apt-get install -y libcurl4-openssl-dev libjson-c-dev gcc make

echo "Building frontend..."
cd /home/petr/jetson/phase3/frontend
make clean
make

echo "Frontend built successfully: ./phase3_frontend"
