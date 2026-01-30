# Troubleshooting Guide: Phase IV Deployment

## Common Issues and Solutions

### 1. ImagePullBackOff Error
**Problem**: Pods show `ImagePullBackOff` status
**Solution**: 
- Ensure Docker images are built in the Minikube Docker environment
- Run: `eval $(minikube docker-env)` before building images
- Verify image exists: `docker images | grep todo-chatbot`

### 2. Minikube Resource Issues
**Problem**: Insufficient CPU or memory
**Solution**:
- Increase Minikube resources: `minikube start --cpus=4 --memory=8192`
- Check current allocation: `minikube ssh 'free -h'`

### 3. Helm Installation Failures
**Problem**: Helm install fails with dependency or configuration errors
**Solution**:
- Update Helm repositories: `helm repo update`
- Check chart validity: `helm lint deployments/helm-charts/todo-chatbot-[frontend|backend]`
- Dry-run installation: `helm install [name] [chart] --dry-run`

### 4. Service Connectivity Issues
**Problem**: Frontend cannot connect to backend service
**Solution**:
- Verify backend service name: `kubectl get svc`
- Check DNS resolution: `kubectl exec -it [frontend-pod] -- nslookup todo-chatbot-backend`
- Verify network policies allow communication

### 5. Persistent Volume Issues
**Problem**: Data not persisting across pod restarts
**Solution**:
- Check PVC binding: `kubectl get pvc`
- Verify PV exists: `kubectl get pv`
- Check storage class: `kubectl get storageclass`

### 6. Health Check Failures
**Problem**: Pods stuck in "ContainerCreating" or "CrashLoopBackOff"
**Solution**:
- Adjust probe settings in Helm values
- Check application startup time
- Verify health check endpoint exists

## Diagnostic Commands

### Check Cluster Status
```bash
kubectl cluster-info
kubectl get nodes
kubectl top nodes
```

### Check Application Status
```bash
kubectl get pods -o wide
kubectl get svc
kubectl get pvc
kubectl get networkpolicy
```

### View Logs
```bash
kubectl logs -l app=todo-chatbot-backend --previous
kubectl logs -l app=todo-chatbot-frontend --previous
kubectl describe pod -l app=todo-chatbot-backend
```

### Network Diagnostics
```bash
kubectl run test-curl --image=curlimages/curl -it --rm --restart=Never -- curl -v http://todo-chatbot-backend:7860/health
```

## Using kubectl-ai for Diagnostics

```bash
# Get help understanding cluster state
kubectl ai "show me the status of all pods in default namespace"

# Troubleshoot specific issues
kubectl ai "why is pod todo-chatbot-backend-xxxxx not ready?"

# Get resource recommendations
kubectl ai "suggest resource optimizations for todo-chatbot-backend deployment"
```

## Recovery Procedures

### Rollback Deployment
```bash
helm rollback todo-chatbot-backend
helm rollback todo-chatbot-frontend
```

### Uninstall and Reinstall
```bash
helm uninstall todo-chatbot-frontend
helm uninstall todo-chatbot-backend
# Reinstall following deployment instructions
```

### Reset Minikube
```bash
minikube delete
minikube start --cpus=2 --memory=4096
```