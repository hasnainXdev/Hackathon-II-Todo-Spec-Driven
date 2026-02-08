# Event-Driven Todo Chatbot System - Phase 5

## Overview

This is the Phase 5 implementation of the Event-Driven Todo Chatbot System. It demonstrates real-world distributed systems using Kafka, Docker Compose, and microservices. The system transforms the monolithic architecture from previous phases into a fully event-driven system with multiple microservices that communicate asynchronously via Kafka events.

## Architecture

### Services
1. **Chat API Service** - Handles user requests and chat commands, publishes events to Kafka
2. **Notification Service** - Consumes reminder events from Kafka and sends notifications
3. **Recurring Task Service** - Processes task completion events and generates recurring tasks
4. **Audit Service** - Consumes all events and maintains immutable audit trail
5. **Sync Service** - Provides real-time updates via WebSockets

### Infrastructure
- **Kafka** - Event backbone using Confluent Kafka
- **PostgreSQL** - Primary data storage
- **Docker Compose** - Local container orchestration

## Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Node.js 18+ (for frontend)

## Directory Structure

```
phase-5/
├── services/
│   ├── chat-api/              # Main API service
│   ├── notification-service/  # Notification handling
│   ├── recurring-task-service/ # Recurring task logic
│   ├── audit-service/         # Audit trail
│   └── sync-service/          # Real-time sync
├── frontend/                 # Next.js frontend
├── specs/                    # Specifications
├── scripts/                  # Utility scripts
├── docker-compose.yml        # Docker Compose orchestration
└── test_services_setup.sh    # Test script
```

## Local Development Setup (Recommended Method)

### 1. Clone and Navigate to Project

```bash
cd /mnt/d/it-course/hackathons/hackathon-II-todo-spec-driven/phase-5
```

### 2. Start All Services with Docker Compose

```bash
# Build and start all services
docker compose up --build

# Or run in detached mode
docker compose up --build -d
```

This will start:
- PostgreSQL database
- Kafka and Zookeeper
- Chat API Service (port 8000)
- Audit Service
- Recurring Task Service
- Notification Service
- Sync Service (port 8001)
- Frontend (port 3000)

### 3. Access the Application

Once all services are running:
- **Frontend**: http://localhost:3000
- **Chat API**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **Sync Service**: http://localhost:8001

## Alternative: Manual Service Startup

If you prefer to run services individually:

### 1. Start Infrastructure Services

```bash
# Start PostgreSQL and Kafka separately
docker run --name todo-postgres -e POSTGRES_DB=todo_app -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres:15

# Start Zookeeper
docker run --name zookeeper -e ZOOKEEPER_CLIENT_PORT=2181 -e ZOOKEEPER_TICK_TIME=2000 -p 2181:2181 -d confluentinc/cp-zookeeper:latest

# Start Kafka
docker run --name kafka --link zookeeper:zookeeper -e KAFKA_BROKER_ID=1 -e KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181 -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092 -e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 -e KAFKA_AUTO_CREATE_TOPICS_ENABLE=true -p 9092:9092 -d confluentinc/cp-kafka:latest
```

### 2. Run Individual Services

For each service, navigate to its directory and install dependencies:

```bash
# Chat API Service
cd services/chat-api
pip install -r requirements.txt
uvicorn src.main:app --host 0.0.0.0 --port 8000

# Audit Service
cd services/audit-service
pip install -r requirements.txt
python src/main.py

# Recurring Task Service
cd services/recurring-task-service
pip install -r requirements.txt
python src/main.py

# Notification Service
cd services/notification-service
pip install -r requirements.txt
python src/main.py

# Sync Service
cd services/sync-service
pip install -r requirements.txt
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### 3. Run Frontend

```bash
cd frontend
npm install
npm run dev
```

## Frontend Configuration

The frontend is configured to communicate with the services:

- `NEXT_PUBLIC_FASTAPI_API_URL`: Points to Chat API service at `http://chat-api:8000/api/v1` (in Docker) or `http://localhost:8000/api/v1` (locally)
- `NEXT_PUBLIC_BETTER_AUTH_URL`: Authentication endpoint
- `NEXT_PUBLIC_CHATKIT_API_URL`: Chat functionality endpoint

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
python3 verify_system.py
```

### Manual Testing

1. Access the frontend at `http://localhost:3000`
2. Register/login to the application
3. Create a task using the form or chat interface
4. Verify that the task appears in the task list
5. Complete a task and verify it's marked as completed
6. Create a recurring task and verify it generates new tasks
7. Check the audit trail for all operations
8. Verify real-time updates via WebSocket connections

## Verification Commands

### Check Service Status

```bash
# Check running containers
docker compose ps

# Check logs for all services
docker compose logs

# Check logs for specific service
docker compose logs chat-api
docker compose logs audit-service
docker compose logs recurring-task-service
docker compose logs notification-service
docker compose logs sync-service
docker compose logs frontend
```

### Check Kafka Topics

```bash
# List Kafka topics
docker exec -it kafka kafka-topics --bootstrap-server localhost:9092 --list

# Check specific topic
docker exec -it kafka kafka-topics --bootstrap-server localhost:9092 --describe --topic task-events
```

### Test Kafka Connectivity

```bash
# Produce a test message to task-events topic
docker exec -it kafka kafka-console-producer --bootstrap-server localhost:9092 --topic task-events

# Consume messages from task-events topic
docker exec -it kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic task-events --from-beginning
```

## Configuration

### Environment Variables

#### Backend Services
- `DATABASE_URL` - PostgreSQL connection string
- `KAFKA_BOOTSTRAP_SERVERS` - Kafka broker addresses

#### Frontend
- `NEXT_PUBLIC_FASTAPI_API_URL` - Backend API URL (defaults to http://chat-api:8000/api/v1 in Docker)
- `NEXT_PUBLIC_BETTER_AUTH_URL` - Authentication service URL
- `NEXT_PUBLIC_CHATKIT_API_URL` - Chat functionality URL

## Troubleshooting

### Common Issues

1. **Services won't start**
   - Check if Docker daemon is running
   - Verify all dependencies are installed
   - Check logs with `docker-compose logs <service-name>`

2. **Kafka Connection Issues**
   - Ensure Kafka and Zookeeper are running
   - Check if services can reach Kafka at `kafka:9092`
   - Verify network connectivity between containers

3. **Database Connection Issues**
   - Verify PostgreSQL is running and accessible
   - Check database credentials in docker-compose.yml
   - Ensure database migration has run successfully

4. **Frontend can't connect to backend**
   - Verify NEXT_PUBLIC_FASTAPI_API_URL is set correctly
   - Check if Chat API service is running on port 8000
   - Ensure CORS settings allow frontend requests

### Diagnostic Commands

```bash
# Check all running containers
docker ps

# Check container networks
docker network ls

# Check specific container logs
docker logs <container-name>

# Execute commands inside a container
docker exec -it <container-name> /bin/bash
```

## Stopping Services

### Stop All Services

```bash
# Stop all services (Ctrl+C in terminal where docker compose up was run)
# Or in detached mode:
docker compose down

# Stop all services and remove volumes
docker compose down -v
```

## Development Notes

### Microservices Architecture Benefits

1. **Decoupled Services**: Each service handles specific responsibilities independently
2. **Event-Driven**: Services communicate through Kafka events, ensuring loose coupling
3. **Scalability**: Individual services can be scaled based on demand
4. **Maintainability**: Each service can be developed, tested, and deployed independently

### Service Communication Flow

1. User interacts with frontend
2. Frontend sends requests to Chat API service
3. Chat API processes requests and publishes events to Kafka
4. Other services consume relevant events from Kafka
5. Services update their respective data stores
6. Sync service pushes real-time updates to frontend via WebSockets

## Migration from Old Backend

The old monolithic `/backend` directory has been replaced with the new microservices architecture. All functionality has been distributed across specialized services:

- Task management → Chat API Service
- Event processing → All services consume from Kafka
- Audit logging → Audit Service
- Recurring tasks → Recurring Task Service
- Notifications → Notification Service
- Real-time sync → Sync Service

## Security

### Authentication
- Uses BetterAuth for user authentication
- JWT tokens for API authentication
- Secure session management

### Data Protection
- Encrypted communication between services
- Secure credential storage in environment variables
- Proper isolation between services

## Monitoring and Observability

### Health Checks

Each service exposes a health check endpoint:
- Chat API: `GET /health` (available at http://localhost:8000/health)
- Sync Service: `GET /health` (available at http://localhost:8001/health)

### Logging

All services log to stdout/stderr, which can be viewed using:
```bash
docker-compose logs <service-name>
```

## Cleanup

### Stop and Remove All Containers

```bash
# Stop and remove all containers, networks, and volumes
docker compose down -v
```

### Remove Docker Images (Optional)

```bash
# Remove all service images
docker rmi todo-chat-api todo-audit-service todo-recurring-task-service todo-notification-service todo-sync-service frontend
```