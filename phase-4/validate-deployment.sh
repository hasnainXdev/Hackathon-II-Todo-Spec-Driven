#!/bin/bash

# Final validation script for Todo Chatbot deployment

echo "=== Validating Todo Chatbot Deployment ==="

echo "1. Checking cluster status..."
kubectl cluster-info
echo

echo "2. Checking nodes..."
kubectl get nodes
echo

echo "3. Checking pods status..."
kubectl get pods
echo

echo "4. Checking services..."
kubectl get services
echo

echo "5. Checking persistent volumes..."
kubectl get pvc
echo

echo "6. Checking network policies..."
kubectl get networkpolicy
echo

echo "7. Checking deployments..."
kubectl get deployments
echo

echo "8. Checking backend pod logs for errors..."
kubectl logs -l app.kubernetes.io/name=todo-chatbot-backend --tail=10
echo

echo "9. Checking frontend pod logs for errors..."
kubectl logs -l app.kubernetes.io/name=todo-chatbot-frontend --tail=10
echo

echo "10. Verifying deployment configuration..."
echo "Backend:"
kubectl describe deployment todo-chatbot-backend
echo
echo "Frontend:"
kubectl describe deployment todo-chatbot-frontend
echo

echo "=== Validation Complete ==="
echo "If all resources show healthy status, the deployment was successful."