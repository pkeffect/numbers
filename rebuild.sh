#!/bin/bash
echo "🔄 Rebuilding Pi Storage System..."
docker-compose down
docker-compose build --no-cache
docker-compose up
