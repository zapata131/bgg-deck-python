#!/bin/bash

# Ensure we are in the project directory
cd "$(dirname "$0")"

# Check if .venv exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install Node dependencies
echo "Installing Node dependencies..."
npm install

# Build Tailwind CSS
echo "Building Tailwind CSS..."
npm run build

# Initialize Database
echo "Initializing Database..."
flask db upgrade

# Run the application
echo "Starting Flask server..."
flask run
