# Quickstart Guide: Phase IV - Cloud-Native Todo Chatbot Deployment

## Prerequisites
- Docker installed and running
- Minikube installed (version 1.20 or higher)
- kubectl installed (version 1.20 or higher)
- kubectl-ai plugin installed
- Docker AI Agent (Gordon) available
- kagent for cluster analysis

## Setup Instructions

### 1. Start Minikube
```bash
minikube start --cpus=2 --memory=4096
```

### 2. Enable Required Minikube Addons
```bash
minikube addons enable ingress
minikube addons enable metrics-server
```

### 3. Verify Environment
```bash
kubectl cluster-info
minikube status
```

## Deployment Steps

### 1. Navigate to Phase 3 Directory
```bash
cd ../phase-3
```

### 2. Build Docker Images Using Gordon
```bash
# Use Docker AI Agent (Gordon) to generate optimized Dockerfiles
# Then build the images for both frontend and backend
docker build -t todo-chatbot-frontend:latest -f frontend/Dockerfile .
docker build -t todo-chatbot-backend:latest -f backend/Dockerfile .
```

### 3. Load Images into Minikube
```bash
# Configure Docker to use Minikube's containerd
eval $(minikube docker-env)

# Rebuild images so they're available to Minikube
docker build -t todo-chatbot-frontend:latest -f frontend/Dockerfile .
docker build -t todo-chatbot-backend:latest -f backend/Dockerfile .
```

### 4. Create Helm Charts
```bash
helm create todo-chatbot-frontend
helm create todo-chatbot-backend
```

### 5. Customize Helm Charts
Update the Helm charts with appropriate configurations for:
- Resource requirements (based on standard local development resources)
- Service communication (internal cluster networking)
- Persistent storage (for backend data)
- Security contexts and network policies

### 6. Deploy Using Helm
```bash
helm install todo-chatbot-frontend ./todo-chatbot-frontend
helm install todo-chatbot-backend ./todo-chatbot-backend
```

### 7. Verify Deployment
```bash
kubectl get pods
kubectl get services
kubectl get pvc
```

### 8. Access the Application
```bash
minikube service todo-chatbot-frontend --url
```

## Validation Commands
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
- Ensure Docker images are built in the Minikube environment with `eval $(minikube docker-env)`
- Check that all required tools (Minikube, kubectl, Helm, kubectl-ai) are properly installed

## Lessons Learned
- Building multi-stage Docker images in resource-constrained environments can take significant time
- Proper user management in containers requires attention to distribution-specific commands
- Helm charts provide excellent configuration management but require careful template validation
- Network policies are essential for securing service-to-service communication
- Persistent volumes require proper storage class configuration in Minikube
- AI-assisted tools like kubectl-ai can significantly speed up diagnostic tasks