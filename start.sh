#!/bin/bash

echo "🥧 Starting Pi Storage System..."

# Check if pi file exists
if [ ! -f "data/pi_1billion.txt" ]; then
    echo "⚠️  WARNING: data/pi_1billion.txt not found!"
    echo "   Please place your pi file in the data/ directory"
    echo "   The system will still start but won't function until the file is added"
fi

# Start the development environment
echo "🐳 Starting Docker containers..."
docker-compose up --build

