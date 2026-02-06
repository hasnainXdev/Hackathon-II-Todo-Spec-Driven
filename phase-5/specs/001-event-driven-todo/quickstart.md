# Quickstart Guide: Event-Driven Todo Chatbot System

## Overview
This guide provides instructions for setting up, running, and verifying the event-driven Todo Chatbot system locally using Minikube. Building upon the AI-powered todo chatbot from Phase 3 and the Kubernetes deployment strategies from Phase 4, this system transforms the monolithic architecture into a fully event-driven system with Kafka, Dapr, and Kubernetes.

## Prerequisites
- Docker (v20.10+)
- Minikube (v1.28+) - from Phase 4
- kubectl (v1.25+)
- Python 3.11+ - from Phase 3
- Dapr CLI (v1.9+)
- Git

## Local Setup

### 1. Clone and Navigate to Repository
```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Install Dapr
```bash
dapr init
```

### 3. Start Minikube Cluster (from Phase 4)
```bash
minikube start --memory=8192 --cpus=4
```

### 4. Enable Required Minikube Add-ons (from Phase 4)
```bash
minikube addons enable ingress
minikube addons enable metrics-server
```

### 5. Deploy Kafka to Minikube (Phase 5 addition)
```bash
# Deploy Strimzi Kafka operator
kubectl create -f https://strimzi.io/install/latest?namespace=kafka -n kafka
kubectl wait --for=condition=ready pod -l name=strimzi-cluster-operator -n kafka

# Create a Kafka cluster
kubectl apply -f infrastructure/k8s/components/kafka/cluster.yaml
kubectl wait --for=condition=ready kafka/my-cluster -n default

# Create required topics
kubectl apply -f infrastructure/k8s/components/kafka/topics/
```

### 6. Deploy PostgreSQL (enhanced from Phase 3's Neon PostgreSQL)
```bash
kubectl apply -f infrastructure/k8s/components/postgres.yaml
kubectl wait --for=condition=ready pod -l app=postgres
```

### 7. Deploy Dapr Components (Phase 5 addition)
```bash
kubectl apply -f infrastructure/dapr/components/
```

### 8. Build and Deploy Services (enhanced from Phase 3's AI chatbot)
```bash
# Build container images
docker build -t todo-chat-api:latest services/chat-api/  # Enhanced from Phase 3's AI chatbot backend
docker build -t todo-recurring-service:latest services/recurring-task-service/
docker build -t todo-notification-service:latest services/notification-service/
docker build -t todo-audit-service:latest services/audit-service/
docker build -t todo-sync-service:latest services/sync-service/

# Push images to Minikube registry (from Phase 4)
eval $(minikube docker-env)
docker build -t todo-chat-api:latest services/chat-api/
docker build -t todo-recurring-service:latest services/recurring-task-service/
docker build -t todo-notification-service:latest services/notification-service/
docker build -t todo-audit-service:latest services/audit-service/
docker build -t todo-sync-service:latest services/sync-service/

# Deploy services to Minikube (from Phase 4)
kubectl apply -f infrastructure/k8s/overlays/minikube/
```

## Verification Steps

### 1. Check Service Status
```bash
kubectl get pods
kubectl get services
kubectl get kafka
```

### 2. Verify Kafka Topics
```bash
kubectl exec -it my-cluster-kafka-0 -- bin/kafka-topics.sh --bootstrap-server localhost:9092 --list
```

### 3. Test Chat API (enhanced from Phase 3)
```bash
# Forward Chat API port
kubectl port-forward svc/chat-api-service 8000:80

# Send a test command (similar to Phase 3's chat interface)
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"command": "Add task: Test task from quickstart", "userId": "test-user-123"}'
```

### 4. Verify Event Flow (Phase 5 addition)
```bash
# Check Chat API logs for event publishing
kubectl logs -f deployment/chat-api --since=1m

# Check consumer service logs for event processing
kubectl logs -f deployment/audit-service --since=1m
kubectl logs -f deployment/recurring-task-service --since=1m
kubectl logs -f deployment/notification-service --since=1m
```

## Common Commands

### View All Logs
```bash
# View logs for all services
kubectl logs -f deployment/chat-api      # Enhanced from Phase 3's backend
kubectl logs -f deployment/recurring-task-service
kubectl logs -f deployment/notification-service
kubectl logs -f deployment/audit-service
kubectl logs -f deployment/sync-service   # Enhanced from Phase 3's real-time features
```

### Access Kafka UI (optional)
```bash
kubectl port-forward svc/my-cluster-kafka-external-bootstrap 9094:9094
```

### Access PostgreSQL (for debugging)
```bash
kubectl port-forward svc/postgres-service 5432:5432
# Then connect with your favorite PostgreSQL client
```

## Troubleshooting

### Service Won't Start
- Check if all dependencies (Kafka, PostgreSQL, Dapr) are running
- Verify image names match what's in the deployment files
- Check resource limits in deployment files

### Kafka Connection Issues
- Ensure Kafka cluster is ready: `kubectl wait --for=condition=ready kafka/my-cluster`
- Check if Kafka topics were created successfully
- Verify network policies allow communication

### Dapr Sidecar Missing
- Ensure Dapr is initialized: `dapr init`
- Check if Dapr system services are running: `kubectl get pods -n dapr-system`
- Verify services have Dapr annotations in deployment files

### Phase 3 Integration Issues
- If experiencing issues with chat functionality, verify that the Phase 3 AI backend components are properly integrated
- Check that the conversation and message models are correctly mapped to the event-driven architecture

## Cleanup
```bash
# Delete all resources
kubectl delete -f infrastructure/k8s/overlays/minikube/
kubectl delete -f infrastructure/dapr/components/
kubectl delete -f infrastructure/k8s/components/postgres.yaml
kubectl delete -f infrastructure/k8s/base/
kubectl delete -f infrastructure/k8s/components/kafka/topics/
kubectl delete -f infrastructure/k8s/components/kafka/cluster.yaml

# Stop Minikube
minikube stop
```

## Next Steps
- Explore the API documentation at `/docs` endpoint (from Phase 3's FastAPI)
- Review the event-driven flows in the architecture documentation
- Customize the system for your specific requirements
- Prepare for cloud deployment using the cloud deployment guide (from Phase 4)
- Understand how the Phase 3 AI chatbot functionality integrates with the event-driven architecture