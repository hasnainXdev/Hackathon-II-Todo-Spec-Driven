#!/bin/bash

# Script to deploy the event-driven todo system to a cloud Kubernetes cluster

set -e  # Exit on any error

echo "Deploying event-driven todo system to cloud Kubernetes cluster..."

# Build and push container images to a registry
# Note: You'll need to replace REGISTRY_NAME with your actual container registry

REGISTRY_NAME="your-container-registry"  # Replace with your registry
IMAGE_TAG="latest"

echo "Building and pushing container images..."

# Build and push chat-api
docker build -t $REGISTRY_NAME/todo-chat-api:$IMAGE_TAG services/chat-api/
docker push $REGISTRY_NAME/todo-chat-api:$IMAGE_TAG

# Build and push notification-service
docker build -t $REGISTRY_NAME/todo-notification-service:$IMAGE_TAG services/notification-service/
docker push $REGISTRY_NAME/todo-notification-service:$IMAGE_TAG

# Build and push recurring-task-service
docker build -t $REGISTRY_NAME/todo-recurring-task-service:$IMAGE_TAG services/recurring-task-service/
docker push $REGISTRY_NAME/todo-recurring-task-service:$IMAGE_TAG

# Build and push audit-service
docker build -t $REGISTRY_NAME/todo-audit-service:$IMAGE_TAG services/audit-service/
docker push $REGISTRY_NAME/todo-audit-service:$IMAGE_TAG

# Build and push sync-service
docker build -t $REGISTRY_NAME/todo-sync-service:$IMAGE_TAG services/sync-service/
docker push $REGISTRY_NAME/todo-sync-service:$IMAGE_TAG

echo "Container images pushed successfully!"

# Update the Kubernetes deployment files to use the cloud images
echo "Updating Kubernetes deployment files..."

# Create a temporary directory for the cloud deployments
mkdir -p infrastructure/k8s/cloud

# Copy base deployments to cloud directory and update image references
sed "s|image: todo-chat-api:latest|image: $REGISTRY_NAME/todo-chat-api:$IMAGE_TAG|" infrastructure/k8s/base/chat-api-deployment.yaml > infrastructure/k8s/cloud/chat-api-deployment.yaml
sed "s|image: todo-notification-service:latest|image: $REGISTRY_NAME/todo-notification-service:$IMAGE_TAG|" infrastructure/k8s/base/notification-deployment.yaml > infrastructure/k8s/cloud/notification-deployment.yaml
sed "s|image: todo-recurring-task-service:latest|image: $REGISTRY_NAME/todo-recurring-task-service:$IMAGE_TAG|" infrastructure/k8s/base/recurring-task-deployment.yaml > infrastructure/k8s/cloud/recurring-task-deployment.yaml
sed "s|image: todo-audit-service:latest|image: $REGISTRY_NAME/todo-audit-service:$IMAGE_TAG|" infrastructure/k8s/base/audit-deployment.yaml > infrastructure/k8s/cloud/audit-deployment.yaml
sed "s|image: todo-sync-service:latest|image: $REGISTRY_NAME/todo-sync-service:$IMAGE_TAG|" infrastructure/k8s/base/sync-deployment.yaml > infrastructure/k8s/cloud/sync-deployment.yaml

echo "Kubernetes deployment files updated for cloud deployment!"

# Deploy Kafka to the cloud cluster
echo "Deploying Kafka to cloud cluster..."
kubectl create namespace kafka || true
kubectl apply -f https://strimzi.io/install/latest?namespace=kafka -n kafka
kubectl wait --for=condition=ready pod -l name=strimzi-cluster-operator -n kafka --timeout=300s

# Create Kafka cluster
cat << EOF | kubectl apply -f -
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: my-cluster
  namespace: kafka
spec:
  kafka:
    version: 3.7.0
    replicas: 1
    listeners:
      - name: plain
        port: 9092
        type: internal
        tls: false
      - name: tls
        port: 9093
        type: internal
        tls: true
    config:
      offsets.topic.replication.factor: 1
      transaction.state.log.replication.factor: 1
      transaction.state.log.min.isr: 1
      default.replication.factor: 1
      min.insync.replicas: 1
      inter.broker.protocol.version: "3.7"
    storage:
      type: jbod
      volumes:
      - id: 0
        type: persistent-claim
        size: 10Gi
        deleteClaim: false
  zookeeper:
    replicas: 1
    storage:
      type: persistent-claim
      size: 5Gi
      deleteClaim: false
  entityOperator:
    topicOperator: {}
    userOperator: {}
EOF

kubectl wait --for=condition=ready kafka/my-cluster -n kafka --timeout=600s

# Create required topics
cat << EOF | kubectl apply -f -
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-events
  namespace: kafka
  labels:
    strimzi.io/cluster: my-cluster
spec:
  partitions: 3
  replicas: 1
EOF

cat << EOF | kubectl apply -f -
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: reminders
  namespace: kafka
  labels:
    strimzi.io/cluster: my-cluster
spec:
  partitions: 3
  replicas: 1
EOF

cat << EOF | kubectl apply -f -
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-updates
  namespace: kafka
  labels:
    strimzi.io/cluster: my-cluster
spec:
  partitions: 3
  replicas: 1
EOF

echo "Kafka deployed and topics created!"

# Deploy PostgreSQL to the cloud cluster
echo "Deploying PostgreSQL to cloud cluster..."
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: todo-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:13
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_DB
          value: todo_chatbot
        - name: POSTGRES_USER
          value: user
        - name: POSTGRES_PASSWORD
          value: password
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
      volumes:
      - name: postgres-storage
        emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: postgres-service
  namespace: todo-app
spec:
  selector:
    app: postgres
  ports:
    - protocol: TCP
      port: 5432
      targetPort: 5432
  type: ClusterIP
EOF

echo "PostgreSQL deployed!"

# Deploy Dapr to the cloud cluster
echo "Deploying Dapr to cloud cluster..."
kubectl apply -f https://github.com/dapr/dapr/releases/latest/download/dapr-kubernetes.tar.gz
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=dapr-operator -n dapr-system --timeout=300s

# Apply Dapr components
kubectl apply -f infrastructure/dapr/components/ -n todo-app

echo "Dapr deployed and configured!"

# Deploy the services to the cloud cluster
echo "Deploying services to cloud cluster..."
kubectl apply -f infrastructure/k8s/cloud/ -n todo-app

# Wait for deployments to be ready
kubectl wait --for=condition=ready pod -l app=chat-api -n todo-app --timeout=300s
kubectl wait --for=condition=ready pod -l app=notification-service -n todo-app --timeout=300s
kubectl wait --for=condition=ready pod -l app=recurring-task-service -n todo-app --timeout=300s
kubectl wait --for=condition=ready pod -l app=audit-service -n todo-app --timeout=300s
kubectl wait --for=condition=ready pod -l app=sync-service -n todo-app --timeout=300s

echo "All services deployed and ready!"

echo "Cloud deployment completed successfully!"
echo "Services are running in the 'todo-app' namespace"
echo "Kafka is running in the 'kafka' namespace"
echo "You can access the chat API at: $(kubectl get svc chat-api-service -n todo-app -o jsonpath='{.status.loadBalancer.ingress[0].ip}')"