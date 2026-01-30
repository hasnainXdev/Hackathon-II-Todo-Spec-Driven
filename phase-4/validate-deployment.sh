#!/bin/bash

# Script to validate the deployment of the Todo Chatbot application
set -e

echo "Validating deployment..."

# Check if Docker is installed and running
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed or not in PATH"
    exit 1
fi

# Check if we can run a simple Docker command
docker version > /dev/null || { echo "Docker daemon is not running"; exit 1; }

# Validate frontend Docker build
echo "Building frontend Docker image..."
cd /mnt/d/it-course/hackathons/hackathon-II-todo-spec-driven/phase-4/frontend
docker build -t todo-chatbot-frontend . || { echo "Failed to build frontend Docker image"; exit 1; }

# Validate backend Docker build
echo "Building backend Docker image..."
cd /mnt/d/it-course/hackathons/hackathon-II-todo-spec-driven/phase-4/backend
docker build -t todo-chatbot-backend . || { echo "Failed to build backend Docker image"; exit 1; }

echo "Docker images built successfully!"

# Optional: Test if images can be run (non-blocking)
echo "Testing if containers can start..."
docker run -d --name test-frontend -p 3000:3000 todo-chatbot-frontend || echo "Warning: Could not start frontend container"
docker run -d --name test-backend -p 7860:7860 todo-chatbot-backend || echo "Warning: Could not start backend container"

# Clean up test containers
sleep 5
docker stop test-frontend test-backend > /dev/null 2>&1 || true
docker rm test-frontend test-backend > /dev/null 2>&1 || true

echo "Deployment validation completed successfully!"