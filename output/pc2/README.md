# Chat App - pc2

## Node Information

| Property | Value |
|----------|-------|
| **Name** | pc2 |
| **IP Address** | 192.168.1.11 |
| **Hostname** | pc2.local |
| **Location** | Office - Room 2 |
| **Default Username** | user_pc2 |

## Quick Start

### 1. Setup RabbitMQ Federation

Run as Administrator:
```batch
federation_setup.bat
```

### 2. Start Docker Containers

```batch
start.bat
```

### 3. Access Chat App

```batch
docker exec -it chat_app_pc2 python sync_chatting_app.py
```

## Services

| Service | URL | Credentials |
|---------|-----|-------------|
| RabbitMQ AMQP | `192.168.1.11:5672` | guest/guest |
| RabbitMQ Management | http://192.168.1.11:15672 | guest/guest |

## Connected Peer Nodes (9 nodes)

- **pc1**: 192.168.1.10 (Office - Room 1)
- **pc3**: 192.168.1.12 (Office - Room 3)
- **pc4**: 192.168.1.13 (Office - Room 4)
- **pc5**: 192.168.1.14 (Office - Room 5)
- **pc6**: 192.168.1.15 (Office - Room 6)
- **pc7**: 192.168.1.16 (Office - Room 7)
- **pc8**: 192.168.1.17 (Office - Room 8)
- **pc9**: 192.168.1.18 (Office - Room 9)
- **pc10**: 192.168.1.19 (Office - Room 10)

## Troubleshooting

### Check RabbitMQ Status
```batch
rabbitmqctl status
```

### Verify Federation
```batch
verify_federation.bat
```

### View Docker Logs
```batch
docker-compose logs -f
```

### Restart Services
```batch
stop.bat
start.bat
```

## Files

- `docker-compose.yml` - Docker Compose configuration
- `.env` - Environment variables
- `federation_setup.bat` - RabbitMQ federation setup
- `verify_federation.bat` - Federation verification
- `start.bat` - Start all containers
- `stop.bat` - Stop all containers

---
Generated: 2026-03-20 09:39:31
