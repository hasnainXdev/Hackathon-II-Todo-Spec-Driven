# Phase IV Deployment Documentation

## Overview
This document provides instructions for deploying the Todo Chatbot application to a local Kubernetes cluster using Minikube.

## Live Preview ⭐
[https://taskflow-ai-snowy.vercel.app]

## Prerequisites
- Docker installed and running
- Minikube installed (version 1.20 or higher)
- kubectl installed (version 1.20 or higher)
- kubectl-ai plugin installed
- Helm 3 installed

## Setup Instructions

### 1. Start Minikube
```bash
minikube start --cpus=2 --memory=4096
minikube addons enable ingress
minikube addons enable metrics-server
```

### 2. Build Docker Images
```bash
# Configure Docker to use Minikube's containerd
eval $(minikube docker-env)

# Build the images for both frontend and backend
docker build -t todo-chatbot-frontend:latest -f frontend/Dockerfile .
docker build -t todo-chatbot-backend:latest -f backend/Dockerfile .
```

### 3. Deploy Using Helm
```bash
# Install backend first
helm install todo-chatbot-backend deployments/helm-charts/todo-chatbot-backend --namespace=default --create-namespace

# Install frontend
helm install todo-chatbot-frontend deployments/helm-charts/todo-chatbot-frontend --namespace=default
```

## Architecture
- Frontend: React application served on port 3000
- Backend: Python/FastAPI application serving API on port 7860
- Communication: Internal cluster networking via service DNS
- Storage: Persistent volume for backend data
- Security: Network policies restricting traffic
- Health Checks: Liveness and readiness probes configured

## Verification
```bash
# Check if all pods are running
kubectl get pods

# Check if services are accessible
kubectl get svc

# Verify persistent volumes are bound
kubectl get pvc

# Check application logs
kubectl logs -l app=todo-chatbot-backend
kubectl logs -l app=todo-chatbot-frontend
```

## Troubleshooting
- If pods fail to start, check logs with `kubectl logs <pod-name>`
- If services are not accessible, verify network policies with `kubectl get networkpolicy`
- If storage issues occur, check PVC status with `kubectl get pvc`
- Use `kubectl-ai` for diagnostic operations if issues arise
