#!/bin/bash

# Script to provision a cloud Kubernetes cluster (using Oracle OKE as an example)
# This script assumes you have the OCI CLI installed and configured

set -e  # Exit on any error

echo "Provisioning cloud Kubernetes cluster..."

# Variables
CLUSTER_NAME="todo-event-driven-cluster"
NODE_COUNT=3
SHAPE="VM.Standard2.1"  # Adjust based on your needs and region
REGION="us-ashburn-1"   # Adjust to your preferred region

echo "Creating cluster: $CLUSTER_NAME in region: $REGION"

# Create the cluster
oci ce cluster create \
  --name "$CLUSTER_NAME" \
  --kubernetes-version "v1.28.2" \
  --vcn-name "$CLUSTER_NAME-vcn" \
  --service-lb-subnet-names "$CLUSTER_NAME-svc-lb-subnet1,$CLUSTER_NAME-svc-lb-subnet2" \
  --nodes-subnet-names "$CLUSTER_NAME-nodes-subnet1,$CLUSTER_NAME-nodes-subnet2" \
  --endpoint-config "{\"isPublicIpEnabled\": true}" \
  --wait-for-state "ACTIVE"

echo "Cluster created successfully!"

# Get the kubeconfig
mkdir -p ~/.kube
oci ce cluster create-kubeconfig --cluster-name "$CLUSTER_NAME" --file ~/.kube/config --region "$REGION"

echo "Kubeconfig updated!"

# Create namespaces
kubectl create namespace todo-app || true
kubectl create namespace kafka || true

echo "Cloud cluster provisioning completed!"
echo "Cluster: $CLUSTER_NAME"
echo "Region: $REGION"
echo "Node Count: $NODE_COUNT"
echo "Current context: $(kubectl config current-context)"