# Docker Setup for RabbitMQ SQLite Sync Chat App

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Network                        │
│                  (172.28.0.0/16)                         │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  RabbitMQ    │  │   App A      │  │   App B      │  │
│  │ 172.28.0.2   │  │ 172.28.0.3   │  │ 172.28.0.4   │  │
│  │ :5672        │  │              │  │              │  │
│  │ :15672       │  │              │  │              │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Prerequisites

- Docker Desktop installed dan running
- Windows 10/11 Pro atau Enterprise

## Quick Start

### 1. Start All Services
```bash
start.bat
```

### 2. Access Apps
- **App A**: Connect to container `chat_app_a`
- **App B**: Connect to container `chat_app_b`

### 3. View Logs
```bash
logs.bat
```

### 4. Stop All Services
```bash
stop.bat
```

## Manual Docker Commands

### Start
```bash
docker-compose up -d
```

### View Logs
```bash
# All logs
docker-compose logs -f

# Specific container
docker-compose logs -f app_a
docker-compose logs -f app_b
```

### Stop
```bash
docker-compose down
```

### Restart
```bash
docker-compose restart
```

## RabbitMQ Management UI

- **URL**: http://localhost:15672
- **Username**: guest
- **Password**: guest

## Container IPs

| Container | Hostname | IP Address | Ports |
|-----------|----------|------------|-------|
| rabbitmq  | rabbitmq | 172.28.0.2 | 5672, 15672 |
| app_a     | app_a    | 172.28.0.3 | - |
| app_b     | app_b    | 172.28.0.4 | - |

## Testing 2-Way Communication

1. Start all services: `start.bat`
2. Open terminal to App A container:
   ```bash
   docker exec -it chat_app_a python sync_chatting_app.py
   ```
3. Open another terminal to App B container:
   ```bash
   docker exec -it chat_app_b python sync_chatting_app.py
   ```
4. Send messages from both sides and verify they sync!

## Troubleshooting

### Docker not running
```
[ERROR] Docker is not running!
```
→ Start Docker Desktop first

### Container can't connect to RabbitMQ
```bash
docker-compose restart rabbitmq
```

### Reset everything
```bash
docker-compose down -v
docker-compose up -d
```

## Notes

- Database files (`chat.db`) are persisted via volume mapping
- RabbitMQ messages are NOT persisted (lost on restart)
- Each container has its own IP for network testing
