#!/usr/bin/env bash
# Exit on error
set -o errexit

# 1. Build the React frontend
echo "Building React frontend..."
cd frontend
npm install
npm run build
cd ..

# 2. Install Python backend dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
