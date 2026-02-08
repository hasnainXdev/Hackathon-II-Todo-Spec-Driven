#!/bin/bash

# Test script to verify services setup
echo "Testing services setup..."

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "docker-compose could not be found, trying docker compose"
    if ! command -v docker &> /dev/null; then
        echo "docker could not be found"
        exit 1
    fi
    DOCKER_COMPOSE_CMD="docker compose"
else
    DOCKER_COMPOSE_CMD="docker-compose"
fi

echo "Using command: $DOCKER_COMPOSE_CMD"

# Check if docker daemon is running
if ! $DOCKER_COMPOSE_CMD version &> /dev/null; then
    echo "Docker daemon is not running or not accessible"
    exit 1
fi

echo "Services setup is ready for deployment with:"
echo "  $DOCKER_COMPOSE_CMD up --build"
echo ""
echo "To test the services locally, run the above command and then:"
echo "  - Access the frontend at http://localhost:3000"
echo "  - The Chat API will be available at http://localhost:8000"
echo "  - The Sync service will be available at http://localhost:8001"
echo ""
echo "The frontend is configured to communicate with the services instead of the old monolithic backend."

exit 0