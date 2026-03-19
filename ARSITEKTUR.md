# Dokumen Arsitektur Sistem
## RabbitMQ SQLite Sync Chat Application

---

## 1. Ringkasan Eksekutif

Sistem ini adalah aplikasi **chatting realtime** dengan kemampuan **sinkronisasi database SQLite** antar multiple client menggunakan **RabbitMQ** sebagai message broker. Setiap client berjalan dalam container Docker terisolasi dengan database lokal sendiri, namun semua database tetap sinkron 100% melalui mekanisme event-driven architecture.

---

## 2. Arsitektur Sistem

### 2.1 Diagram Arsitektur Fisik

```
┌─────────────────────────────────────────────────────────────────┐
│                    HOST MACHINE (Windows PC)                    │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                    Docker Desktop                         │ │
│  │                                                           │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │              Docker Network (Bridge)                │ │ │
│  │  │              Subnet: 172.28.0.0/16                  │ │ │
│  │  │                                                     │ │ │
│  │  │  ┌───────────────┐  ┌───────────────┐  ┌─────────┐ │ │ │
│  │  │  │   RabbitMQ    │  │    App A      │  │  App B  │ │ │ │
│  │  │  │   Broker      │  │  Container    │  │Container│ │ │ │
│  │  │  │               │  │               │  │         │ │ │ │
│  │  │  │  172.28.0.2   │  │  172.28.0.3   │  │172.28.0.│ │ │ │
│  │  │  │  :5672        │  │               │  │    4    │ │ │ │
│  │  │  │  :15672       │  │  Python 3.11  │  │Python   │ │ │ │
│  │  │  │               │  │  SQLite       │  │ 3.11    │ │ │ │
│  │  │  │               │  │  chat.db      │  │ SQLite  │ │ │ │
│  │  │  │               │  │               │  │ chat.db │ │ │ │
│  │  │  └───────┬───────┘  └───────┬───────┘  └────┬────┘ │ │ │
│  │  │          │                  │                │      │ │ │
│  │  └──────────┼──────────────────┼────────────────┘      │ │
│  │             │                  │                        │ │
│  └─────────────┼──────────────────┼────────────────────────┘ │
│                │                  │                          │
│                ▼                  ▼                          │
│         localhost:5672     localhost:15672                   │
│         (AMQP)            (Management UI)                    │
└───────────────────────────────────────────────────────────────┘
```

### 2.2 Diagram Arsitektur Logikal

```
┌─────────────────────────────────────────────────────────────────┐
│                     APPLICATION LAYER                           │
│                                                                 │
│  ┌─────────────────────┐           ┌─────────────────────┐     │
│  │      Client A       │           │      Client B       │     │
│  │                     │           │                     │     │
│  │  ┌───────────────┐  │           │  ┌───────────────┐  │     │
│  │  │   Producer    │  │           │  │   Producer    │  │     │
│  │  │  (Publisher)  │  │           │  │  (Publisher)  │  │     │
│  │  └───────┬───────┘  │           │  └───────┬───────┘  │     │
│  │          │          │           │          │          │     │
│  │  ┌───────▼───────┐  │           │  ┌───────▼───────┐  │     │
│  │  │   Consumer    │  │           │  │   Consumer    │  │     │
│  │  │   (Listener)  │  │           │  │   (Listener)  │  │     │
│  │  └───────┬───────┘  │           │  └───────┬───────┘  │     │
│  │          │          │           │          │          │     │
│  │  ┌───────▼───────┐  │           │  ┌───────▼───────┐  │     │
│  │  │  SQLite DB    │  │           │  │  SQLite DB    │  │     │
│  │  │   (Local)     │  │           │  │   (Local)     │  │     │
│  │  └───────────────┘  │           │  └───────────────┘  │     │
│  └──────────┬──────────┘           └──────────┬──────────┘     │
│             │                                 │                │
└─────────────┼─────────────────────────────────┼────────────────┘
              │                                 │
              │         PUBLISH                 │
              │────────────────────────────────►│
              │                                 │
              │         PUBLISH                 │
              │◄────────────────────────────────│
              │                                 │
              ▼                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      MESSAGE LAYER                              │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                    RabbitMQ Broker                        │ │
│  │                                                           │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │           Exchange: chat_exchange                   │ │ │
│  │  │           Type: fanout (broadcast)                  │ │ │
│  │  │           Durable: Yes                              │ │ │
│  │  │                                                     │ │ │
│  │  │  ┌──────────────────────────────────────────────┐  │ │ │
│  │  │  │              Queue (auto-delete)             │  │ │ │
│  │  │  │              - Unique per client             │  │ │ │
│  │  │  │              - Exclusive                     │  │ │ │
│  │  │  └──────────────────────────────────────────────┘  │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 2.3 Diagram Sequence Flow

```
┌────────┐         ┌────────┐         ┌──────────┐         ┌────────┐
│ App A  │         │ App B  │         │ RabbitMQ │         │  DB A  │
└───┬────┘         └───┬────┘         └────┬─────┘         └───┬────┘
    │                  │                    │                   │
    │ Login: user_a    │                    │                   │
    │──────────────────────────────────────►│                   │
    │                  │                    │                   │
    │                  │ Login: user_b      │                   │
    │                  │───────────────────►│                   │
    │                  │                    │                   │
    │                  │  Broadcast Event   │                   │
    │◄───────────────────────────────────────│                   │
    │                  │                    │                   │
    │ [Simpan user_b]  │                    │                   │
    │───────────────────────────────────────────────────────────►│
    │                  │                    │                   │
    │                  │  Broadcast Event   │                   │
    │◄───────────────────────────────────────│                   │
    │                  │                    │                   │
    │ [Simpan user_a]  │                    │                   │
    │                  │───────────────────────────────────────►│
    │                  │                    │                   │
    │ Kirim: "Halo"    │                    │                   │
    │──────────────────────────────────────►│                   │
    │                  │                    │                   │
    │                  │  Broadcast Event   │                   │
    │                  │◄───────────────────│                   │
    │                  │                    │                   │
    │  (Abaikan event  │                    │                   │
    │   sendiri)       │                    │                   │
    │                  │ [Simpan pesan]     │                   │
    │                  │───────────────────────────────────────►│
    │                  │                    │                   │
    │                  │ Kirim: "Hai"       │                   │
    │                  │───────────────────►│                   │
    │                  │                    │                   │
    │  Broadcast Event │                    │                   │
    │◄─────────────────│                    │                   │
    │                  │                    │                   │
    │ [Simpan pesan]   │  (Abaikan event    │                   │
    │─────────────────►│   sendiri)         │                   │
    │                  │                    │                   │
```

---

## 3. Komponen Sistem

### 3.1 Container RabbitMQ Broker

| Properti | Nilai |
|----------|-------|
| **Image** | `rabbitmq:3-management` |
| **Container Name** | `rabbitmq_broker` |
| **Hostname** | `rabbitmq` |
| **IP Address** | `172.28.0.2` |
| **Ports** | `5672` (AMQP), `15672` (Management UI) |
| **Network** | `chat_network` |

**Fungsi:**
- Message broker untuk komunikasi antar client
- Fanout exchange untuk broadcast message ke semua connected client
- Management UI untuk monitoring queue dan exchange

**Konfigurasi Exchange:**
```python
exchange_name = 'chat_exchange'
exchange_type = 'fanout'
durable = True
```

### 3.2 Container App A

| Properti | Nilai |
|----------|-------|
| **Image** | Custom build (Python 3.11-slim) |
| **Container Name** | `chat_app_a` |
| **Hostname** | `app_a` |
| **IP Address** | `172.28.0.3` |
| **Volume** | `./A:/app`, `./A/chat.db:/app/chat.db` |
| **Environment** | `RABBITMQ_HOST=rabbitmq` |

**Fungsi:**
- Chat client instance pertama
- Producer: mengirim event user login dan pesan
- Consumer: menerima dan memproses event dari client lain
- SQLite database lokal untuk penyimpanan pesan

### 3.3 Container App B

| Properti | Nilai |
|----------|-------|
| **Image** | Custom build (Python 3.11-slim) |
| **Container Name** | `chat_app_b` |
| **Hostname** | `app_b` |
| **IP Address** | `172.28.0.4` |
| **Volume** | `./B:/app`, `./B/chat.db:/app/chat.db` |
| **Environment** | `RABBITMQ_HOST=rabbitmq` |

**Fungsi:** Sama dengan App A (instance kedua)

---

## 4. Database Schema

### 4.1 Tabel `messages`

```sql
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    text TEXT,
    timestamp TEXT,
    UNIQUE(username, timestamp, text)
);
```

| Kolom | Tipe | Deskripsi |
|-------|------|-----------|
| `id` | INTEGER | Primary key, auto increment |
| `username` | TEXT | Username pengirim pesan |
| `text` | TEXT | Isi pesan |
| `timestamp` | TEXT | Waktu pesan dikirim (ISO format) |

**Constraint:** `UNIQUE(username, timestamp, text)` untuk mencegah duplikasi

### 4.2 Tabel `users`

```sql
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    joined_at TEXT
);
```

| Kolom | Tipe | Deskripsi |
|-------|------|-----------|
| `id` | INTEGER | Primary key, auto increment |
| `username` | TEXT | Username user (unique) |
| `joined_at` | TEXT | Waktu user login pertama kali (ISO format) |

---

## 5. Message Format

### 5.1 Event User Registration

```json
{
  "action": "create",
  "type": "user",
  "sender": "<username>",
  "joined_at": "<ISO timestamp>"
}
```

### 5.2 Event Chat Message

```json
{
  "action": "create",
  "type": "message",
  "sender": "<username>",
  "text": "<pesan>",
  "timestamp": "<ISO timestamp>"
}
```

### 5.3 Properti Pesan RabbitMQ

| Properti | Nilai | Deskripsi |
|----------|-------|-----------|
| `delivery_mode` | `2` | Persistent message (tidak hilang saat restart) |
| `exchange` | `chat_exchange` | Fanout exchange untuk broadcast |
| `routing_key` | `''` | Empty (tidak digunakan untuk fanout) |

---

## 6. Alur Kerja (Workflow)

### 6.1 User Login Flow

```
1. User memasukkan username
2. Aplikasi membuat event "create user"
3. Event dikirim ke RabbitMQ exchange
4. RabbitMQ broadcast ke semua connected client
5. Setiap client menerima event:
   - Jika sender == username lokal → ABAIKAN
   - Jika sender != username lokal → SIMPAN ke tabel users
```

### 6.2 Send Message Flow

```
1. User mengetik dan mengirim pesan
2. Aplikasi membuat event "create message"
3. Event dikirim ke RabbitMQ exchange
4. RabbitMQ broadcast ke semua connected client
5. Setiap client menerima event:
   - Jika sender == username lokal → ABAIKAN
   - Jika sender != username lokal → SIMPAN ke tabel messages
```

### 6.3 Sinkronisasi Logic

```python
# Pseudocode consumer logic
def on_message_received(event):
    if event["sender"] == LOCAL_USERNAME:
        # Ini pesan dari diri sendiri, abaikan
        return
    
    # Ini pesan dari user lain, simpan ke database
    if event["type"] == "message":
        INSERT INTO messages (username, text, timestamp)
        VALUES (event["sender"], event["text"], event["timestamp"])
    
    elif event["type"] == "user":
        INSERT OR IGNORE INTO users (username, joined_at)
        VALUES (event["sender"], event["joined_at"])
```

---

## 7. Network Configuration

### 7.1 Docker Network

```yaml
networks:
  chat_network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.28.0.0/16
```

### 7.2 IP Assignment

| Container | Hostname | IP Address | Purpose |
|-----------|----------|------------|---------|
| `rabbitmq_broker` | `rabbitmq` | `172.28.0.2` | Message broker |
| `chat_app_a` | `app_a` | `172.28.0.3` | Client instance A |
| `chat_app_b` | `app_b` | `172.28.0.4` | Client instance B |

### 7.3 Port Mapping

| Service | Container Port | Host Port | Protocol |
|---------|---------------|-----------|----------|
| RabbitMQ AMQP | `5672` | `5672` | TCP |
| RabbitMQ Management | `15672` | `15672` | HTTP |

---

## 8. Deployment

### 8.1 Prerequisites

- Docker Desktop terinstall dan running
- Windows 10/11 Pro atau Enterprise
- RAM minimum 4GB
- Storage minimum 2GB

### 8.2 Quick Start

```bash
# Start semua services
start.bat

# Atau manual
docker-compose up -d

# View logs
docker-compose logs -f

# Stop semua services
docker-compose down
```

### 8.3 Testing

```bash
# Terminal 1 - Connect ke App A
docker exec -it chat_app_a python sync_chatting_app.py

# Terminal 2 - Connect ke App B
docker exec -it chat_app_b python sync_chatting_app.py
```

---

## 9. Monitoring & Troubleshooting

### 9.1 RabbitMQ Management UI

- **URL:** http://localhost:15672
- **Username:** `guest`
- **Password:** `guest`

**Monitoring:**
- Connections count
- Channels count
- Exchanges status
- Queues status
- Message rates

### 9.2 Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Container tidak start | RabbitMQ belum healthy | Tunggu healthcheck passed |
| Tidak bisa connect ke RabbitMQ | Network issue | Restart docker-compose |
| Database tidak sinkron | Consumer error | Cek log consumer |
| Message hilang | Non-persistent | Pastikan delivery_mode=2 |

### 9.3 Log Commands

```bash
# Semua logs
docker-compose logs -f

# Specific container
docker-compose logs -f app_a
docker-compose logs -f app_b
docker-compose logs -f rabbitmq

# Last 50 lines
docker-compose logs --tail=50
```

---

## 10. Scalability & Extension

### 10.1 Menambah Client Baru

Untuk menambah instance client baru (App C, D, dst):

```yaml
app_c:
  build:
    context: ./C
    dockerfile: ../Dockerfile
  container_name: chat_app_c
  hostname: app_c
  networks:
    - chat_network
  volumes:
    - ./C:/app
    - ./C/chat.db:/app/chat.db
  depends_on:
    rabbitmq:
      condition: service_healthy
  environment:
    - PYTHONUNBUFFERED=1
    - RABBITMQ_HOST=rabbitmq
  stdin_open: true
  tty: true
```

### 10.2 Deploy ke Multiple Physical Machines

```
┌──────────────────┐              ┌──────────────────┐
│   Server (PC 1)  │              │   Client (PC 2)  │
│                  │              │                  │
│  ┌────────────┐ │              │  ┌────────────┐ │
│  │ RabbitMQ   │ │              │  │  Chat App  │ │
│  │ :5672      │◄───────────────┼──┤            │ │
│  │ :15672     │ │   LAN/VPN    │  │  chat.db   │ │
│  └────────────┘ │              │  └────────────┘ │
│  ┌────────────┐ │              │                  │
│  │  Chat App  │ │              │                  │
│  └────────────┘ │              │                  │
└──────────────────┘              └──────────────────┘
```

**Konfigurasi:**
1. Server: RabbitMQ dengan public IP atau port forwarding
2. Client: Set `RABBITMQ_HOST=<server-ip>`

---

## 11. Security Considerations

### 11.1 Current State (Development)

- Default credentials: `guest/guest`
- Network: Bridge (isolated)
- No TLS/SSL encryption

### 11.2 Production Recommendations

1. **Authentication:**
   - Ganti default credentials
   - Buat user terpisah per aplikasi

2. **Network:**
   - Gunakan overlay network untuk multi-host
   - Implementasi firewall rules

3. **Encryption:**
   - Enable TLS untuk AMQP (port 5671)
   - Enable HTTPS untuk Management UI

4. **Persistence:**
   - Mount RabbitMQ data volume
   - Enable message persistence

---

## 12. File Structure

```
sc_rabbitmq_sqlite_sync_app/
├── docker-compose.yml          # Docker Compose configuration
├── Dockerfile                  # Base image untuk chat app
├── start.bat                   # Script untuk start semua containers
├── stop.bat                    # Script untuk stop semua containers
├── logs.bat                    # Script untuk view logs
├── test_chat.py               # Automated test script
├── check_db.py                # Database checker script
├── ARSITEKTUR.md              # Dokumen ini
├── README_DOCKER.md           # Docker user guide
├── brief.txt                  # Project brief
│
├── A/                          # App Instance A
│   ├── sync_chatting_app.py   # Main application code
│   ├── requirements.txt       # Python dependencies
│   └── chat.db                # SQLite database
│
└── B/                          # App Instance B
    ├── sync_chatting_app.py   # Main application code
    ├── requirements.txt       # Python dependencies
    └── chat.db                # SQLite database
```

---

## 13. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-18 | Initial architecture |
| 1.1 | 2026-03-19 | Added automated testing, fixed Docker Compose version warning |

---

## 14. Contact & Support

Untuk pertanyaan atau issue terkait arsitektur sistem ini.

---

**Dokumen ini dibuat untuk keperluan dokumentasi teknis sistem RabbitMQ SQLite Sync Chat Application.**
