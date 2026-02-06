# Event-Driven Todo Chatbot System - Phase 5

## Overview

This is the Phase 5 implementation of the Event-Driven Todo Chatbot System. It demonstrates real-world distributed systems using Kafka, Kubernetes, and Dapr. The system transforms the monolithic architecture from previous phases into a fully event-driven system with multiple microservices that communicate asynchronously via Kafka events.

## Architecture

### Services
1. **Chat API Service** - Handles user requests and chat commands, publishes events to Kafka
2. **Notification Service** - Consumes reminder events from Kafka and sends notifications
3. **Recurring Task Service** - Processes task completion events and generates recurring tasks
4. **Audit Service** - Consumes all events and maintains immutable audit trail
5. **Sync Service** - Provides real-time updates via WebSockets

### Infrastructure
- **Kafka** - Event backbone using Strimzi operator
- **PostgreSQL** - Primary data storage
- **Dapr** - State and secret management only
- **Kubernetes** - Container orchestration

## Prerequisites

- Docker and Docker Compose
- Kubernetes cluster (Minikube for local development)
- kubectl
- Helm (optional)
- Python 3.11+

## Directory Structure

```
phase-5/
├── services/
│   ├── chat-api/              # Main API service
│   ├── notification-service/  # Notification handling
│   ├── recurring-task-service/ # Recurring task logic
│   ├── audit-service/         # Audit trail
│   └── sync-service/          # Real-time sync
├── infrastructure/
│   ├── k8s/                  # Kubernetes manifests
│   ├── dapr/                 # Dapr components
│   └── helm/                 # Helm charts
├── frontend/                 # Next.js frontend
├── specs/                    # Specifications
├── scripts/                  # Utility scripts
└── docker/                   # Docker configurations
```

## Local Development Setup

### 1. Start Minikube

```bash
minikube start --memory=8192 --cpus=4
minikube addons enable ingress
minikube addons enable metrics-server
```

### 2. Deploy Kafka to Minikube

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

### 3. Deploy PostgreSQL

```bash
kubectl apply -f infrastructure/k8s/components/postgres.yaml
kubectl wait --for=condition=ready pod -l app=postgres
```

### 4. Deploy Dapr Components

```bash
kubectl apply -f infrastructure/dapr/components/
```

### 5. Build and Deploy Services

```bash
# Build container images
cd services/chat-api/
docker build -t todo-chat-api:latest .
cd ../notification-service/
docker build -t todo-notification-service:latest .
cd ../recurring-task-service/
docker build -t todo-recurring-task-service:latest .
cd ../audit-service/
docker build -t todo-audit-service:latest .
cd ../sync-service/
docker build -t todo-sync-service:latest .

# Push images to Minikube registry
eval $(minikube docker-env)
docker build -t todo-chat-api:latest ../chat-api/
docker build -t todo-notification-service:latest ../notification-service/
docker build -t todo-recurring-task-service:latest ../recurring-task-service/
docker build -t todo-audit-service:latest ../audit-service/
docker build -t todo-sync-service:latest ../sync-service/

# Deploy services to Minikube
kubectl apply -f infrastructure/k8s/overlays/minikube/
```

### 6. Deploy Frontend

```bash
cd frontend
npm install
npm run dev
```

## Cloud Deployment

### 1. Provision Cloud Kubernetes Cluster

```bash
# For Oracle Cloud Infrastructure
./scripts/provision-cloud-cluster.sh

# Or manually create your cluster on your preferred cloud provider
```

### 2. Deploy to Cloud

```bash
./scripts/deploy-to-cloud.sh
```

## Testing

### Unit Tests

```bash
# Test Chat API Service
cd services/chat-api
python3 -m pytest tests/

# Test Notification Service
cd services/notification-service
python3 -m pytest tests/

# Test Recurring Task Service
cd services/recurring-task-service
python3 -m pytest tests/

# Test Audit Service
cd services/audit-service
python3 -m pytest tests/

# Test Sync Service
cd services/sync-service
python3 -m pytest tests/
```

### Integration Tests

```bash
# Run end-to-end verification
python3 scripts/verify-system.py
```

### Manual Testing

1. Access the frontend at `http://localhost:3000`
2. Register/login to the application
3. Create a task using the form or chat interface
4. Verify that the task appears in the task list
5. Complete a task and verify it's marked as completed
6. Create a recurring task and verify it generates new tasks
7. Set a reminder and verify notifications are received
8. Check the audit trail for all operations

## Verification Commands

### Check Service Status

```bash
kubectl get pods
kubectl get services
kubectl get kafka
```

### Check Kafka Topics

```bash
kubectl exec -it my-cluster-kafka-0 -- bin/kafka-topics.sh --bootstrap-server localhost:9092 --list
```

### Check Service Logs

```bash
# Chat API logs
kubectl logs -f deployment/chat-api --since=1m

# Notification service logs
kubectl logs -f deployment/notification-service --since=1m

# Recurring task service logs
kubectl logs -f deployment/recurring-task-service --since=1m

# Audit service logs
kubectl logs -f deployment/audit-service --since=1m

# Sync service logs
kubectl logs -f deployment/sync-service --since=1m
```

### Test Kafka Connectivity

```bash
# Produce a test message
kubectl exec -it my-cluster-kafka-0 -- bin/kafka-console-producer.sh --bootstrap-server localhost:9092 --topic test-topic

# Consume messages
kubectl exec -it my-cluster-kafka-0 -- bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic test-topic --from-beginning
```

## Configuration

### Environment Variables

#### Backend Services
- `DATABASE_URL` - PostgreSQL connection string
- `KAFKA_BOOTSTRAP_SERVERS` - Kafka broker addresses
- `DAPR_SIDECAR_IP` - Dapr sidecar IP address

#### Frontend
- `NEXT_PUBLIC_FASTAPI_API_URL` - Backend API URL
- `NEXT_PUBLIC_WEBSOCKET_URL` - WebSocket service URL
- `NEXT_PUBLIC_BASE_URL` - Frontend base URL
- `BETTER_AUTH_URL` - Authentication service URL

## Troubleshooting

### Common Issues

1. **Service won't start**
   - Check if all dependencies (Kafka, PostgreSQL, Dapr) are running
   - Verify image names match what's in the deployment files
   - Check resource limits in deployment files

2. **Kafka Connection Issues**
   - Ensure Kafka cluster is ready: `kubectl wait --for=condition=ready kafka/my-cluster`
   - Check if Kafka topics were created successfully
   - Verify network policies allow communication

3. **Dapr Sidecar Missing**
   - Ensure Dapr is initialized: `dapr init`
   - Check if Dapr system services are running: `kubectl get pods -n dapr-system`
   - Verify services have Dapr annotations in deployment files

4. **Database Connection Issues**
   - Verify PostgreSQL is running and accessible
   - Check database credentials in secrets
   - Ensure database migration has run successfully

### Diagnostic Commands

```bash
# Check all resources
kubectl get all -A

# Check events for issues
kubectl get events --sort-by=.metadata.creationTimestamp

# Describe a specific pod for detailed info
kubectl describe pod <pod-name>

# Check resource usage
kubectl top nodes
kubectl top pods
```

## Scaling

### Horizontal Pod Autoscaling

```bash
# Enable HPA for services
kubectl autoscale deployment chat-api --cpu-percent=70 --min=1 --max=10
kubectl autoscale deployment notification-service --cpu-percent=70 --min=1 --max=5
kubectl autoscale deployment recurring-task-service --cpu-percent=70 --min=1 --max=5
```

### Resource Limits

Adjust resource limits in the Kubernetes deployment files:

```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

## Cleanup

### Local Cleanup

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

### Cloud Cleanup

```bash
# Delete cloud resources
kubectl delete ns todo-app
kubectl delete ns kafka
kubectl delete ns dapr-system
```

## Monitoring and Observability

### Health Checks

Each service exposes a health check endpoint:
- Chat API: `GET /health`
- Notification Service: `GET /health`
- Recurring Task Service: `GET /health`
- Audit Service: `GET /health`
- Sync Service: `GET /health`

### Logging

All services log to stdout/stderr, which can be viewed using:
```bash
kubectl logs -f <pod-name>
```

### Metrics

Metrics are available through Kubernetes and can be enhanced with Prometheus/Grafana for more detailed monitoring.

## Security

### Authentication
- Uses BetterAuth for user authentication
- JWT tokens for API authentication
- Secure session management

### Authorization
- Role-based access control
- Per-resource permissions
- API rate limiting

### Secrets Management
- Dapr for secret management
- Encrypted communication between services
- Secure credential storage