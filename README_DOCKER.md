# Docker Setup - RabbitMQ SQLite Sync Chat App

Aplikasi chatting realtime dengan sinkronisasi database SQLite menggunakan RabbitMQ sebagai message broker.

---

## 📋 Prerequisites

- **Docker Desktop** terinstall dan running
- **Windows 10/11 Pro** atau Enterprise
- RAM minimum 4GB

---

## 🚀 Cara Install

### 1. Pastikan Docker Desktop Running

Buka Docker Desktop dan tunggu sampai statusnya **Running** (hijau).

### 2. Clone/Pull Project

Pastikan Anda berada di folder project:
```bash
cd d:\Github\sc_rabbitmq_sqlite_sync_app
```

### 3. Build dan Start Containers

**Opsi A - Menggunakan Script (Recommended):**
```bash
start.bat
```

**Opsi B - Manual dengan Docker Compose:**
```bash
docker compose up -d --build
```

### 4. Verifikasi Containers Running

```bash
docker ps
```

Output yang diharapkan:
```
CONTAINER ID   IMAGE                               STATUS
a29832c52c54   rabbitmq:3-management               Up (healthy)
0058f0720dae   sc_rabbitmq_sqlite_sync_app-app_a   Up
faac0cd6fe2a   sc_rabbitmq_sqlite_sync_app-app_b   Up
```

---

## ▶️ Cara Run Aplikasi Chat

### Metode 1: Interactive Chat (Real-time)

**Terminal 1 - Jalankan App A:**
```bash
docker exec -it chat_app_a python sync_chatting_app.py
```
Masukkan username, contoh: `user_a`

**Terminal 2 - Jalankan App B:**
```bash
docker exec -it chat_app_b python sync_chatting_app.py
```
Masukkan username, contoh: `user_b`

Kirim pesan dari kedua terminal - pesan akan muncul di kedua sisi!

### Metode 2: Automated Test

Jalankan test otomatis untuk verifikasi sinkronisasi:
```bash
python test_chat.py
```

Cek isi database setelah test:
```bash
python check_db.py
```

---

## 📊 Monitoring

### View Logs Real-time

**Semua container:**
```bash
docker compose logs -f
```

**Container spesifik:**
```bash
docker compose logs -f app_a
docker compose logs -f app_b
docker compose logs -f rabbitmq
```

**Script cepat:**
```bash
logs.bat
```

### RabbitMQ Management UI

- **URL:** http://localhost:15672
- **Username:** `guest`
- **Password:** `guest`

Untuk monitoring:
- Connections
- Channels
- Exchanges
- Queues
- Message rates

---

## ⏹️ Cara Stop

### Stop Sementara (Pause)

```bash
docker compose stop
```

Untuk start kembali:
```bash
docker compose start
```

### Stop Full (Hapus Containers)

**Opsi A - Menggunakan Script:**
```bash
stop.bat
```

**Opsi B - Manual:**
```bash
docker compose down
```

### Reset Total (Hapus + Volume Database)

```bash
docker compose down -v
```

⚠️ **Warning:** Ini akan menghapus semua data database (`chat.db`)!

---

## 🏗️ Arsitektur

```
┌─────────────────────────────────────────────────────┐
│              Docker Network (172.28.0.0/16)         │
│                                                     │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐     │
│  │ RabbitMQ │    │  App A   │    │  App B   │     │
│  │ 172.28.0.2│    │172.28.0.3│    │172.28.0.4│     │
│  │ :5672    │    │          │    │          │     │
│  │ :15672   │    │ chat.db  │    │ chat.db  │     │
│  └────┬─────┘    └────┬─────┘    └────┬─────┘     │
│       │               │               │            │
│       └───────────────┼───────────────┘            │
│                       │                            │
│              ┌────────▼────────┐                   │
│              │  chat_exchange  │                   │
│              │  (fanout)       │                   │
│              └─────────────────┘                   │
└─────────────────────────────────────────────────────┘
```

### Container Info

| Container | Hostname | IP | Ports |
|-----------|----------|-----|-------|
| `rabbitmq_broker` | rabbitmq | 172.28.0.2 | 5672, 15672 |
| `chat_app_a` | app_a | 172.28.0.3 | - |
| `chat_app_b` | app_b | 172.28.0.4 | - |

---

## 🔧 Troubleshooting

### Container tidak start

```bash
# Cek status
docker ps -a

# Restart semua
docker compose restart

# Reset total
docker compose down -v
docker compose up -d --build
```

### RabbitMQ tidak accessible

```bash
# Cek health
docker compose ps

# Restart RabbitMQ
docker compose restart rabbitmq
```

### App tidak bisa connect ke RabbitMQ

Pastikan environment variable benar:
```bash
docker exec chat_app_a env | grep RABBITMQ
# Harus: RABBITMQ_HOST=rabbitmq
```

### Database tidak sinkron

1. Cek log consumer:
```bash
docker compose logs -f app_a
docker compose logs -f app_b
```

2. Cek isi database:
```bash
python check_db.py
```

3. Reset dan test ulang:
```bash
docker compose down -v
docker compose up -d --build
python test_chat.py
```

### Docker tidak running

```
Error: Docker is not running!
```

**Solusi:** Buka Docker Desktop dan tunggu sampai status **Running**.

---

## 📁 Struktur Project

```
sc_rabbitmq_sqlite_sync_app/
├── docker-compose.yml          # Docker configuration
├── Dockerfile                  # Base image
├── start.bat                   # Quick start script
├── stop.bat                    # Quick stop script
├── logs.bat                    # Quick logs script
├── test_chat.py               # Automated test
├── check_db.py                # Database checker
├── ARSITEKTUR.md              # Dokumen arsitektur lengkap
├── README_DOCKER.md           # Dokumen ini
│
├── A/                          # App Instance A
│   ├── sync_chatting_app.py
│   ├── requirements.txt
│   └── chat.db
│
└── B/                          # App Instance B
    ├── sync_chatting_app.py
    ├── requirements.txt
    └── chat.db
```

---

## 📝 Catatan Penting

- ✅ **Database SQLite** di setiap container **terpisah** tapi **sinkron** via RabbitMQ
- ✅ **Pesan RabbitMQ** tidak persisten (hilang saat restart)
- ✅ **Database** persisten via volume mapping ke file `chat.db` lokal
- ✅ Setiap container punya **IP unik** untuk network testing

---

## 📚 Dokumentasi Lengkap

Untuk detail arsitektur dan cara kerja sistem, lihat: **[ARSITEKTUR.md](ARSITEKTUR.md)**

---

**Version:** 1.1 (2026-03-19)
