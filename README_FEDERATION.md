# RabbitMQ Federation Setup Guide
## Multi-PC Chat Application dengan Sinkronisasi Database

---

## 🚀 Quick Start

**Ingin setup cepat?** Lihat: **[QUICK_START.md](QUICK_START.md)**

---

## 📋 Ringkasan Eksekutif

Guide ini menjelaskan cara setup **RabbitMQ Federation** untuk aplikasi chat multi-PC dengan fitur:

- ✅ **10 PC = 10 RabbitMQ Broker** (setiap PC punya broker sendiri)
- ✅ **Message dikirim PARALLEL** ke semua broker via federation
- ✅ **Tidak ada Single Point of Failure** - jika 1 PC mati, yang lain tetap chat
- ✅ **Sinkronisasi Database SQLite** - semua database sinkron 100%
- ✅ **Config Terpusat** - cukup edit 1 file JSON untuk semua PC

---

## 🏗️ Arsitektur Sistem

```
┌──────────────────────────────────────────────────────────────────┐
│                    FEDERATION MESH NETWORK                       │
│                                                                  │
│  PC 1              PC 2              PC 3         ...   PC 10   │
│  ┌────────────┐   ┌────────────┐   ┌────────────┐     ┌──────┐ │
│  │ RabbitMQ 1 │◄──┤ RabbitMQ 2 │◄──┤ RabbitMQ 3 │  ...│ RMQ10│ │
│  │ + App A    │  │ + App B    │  │ + App C    │     │App 10│ │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘     └──┬───┘ │
│        │               │               │                │      │
│        └───────────────┴───────────────┴────────────────┘      │
│                            │                                    │
│                            ▼                                    │
│              ┌─────────────────────────┐                       │
│              │  FEDERATION EXCHANGE    │                       │
│              │  (Semua Broker Connect) │                       │
│              │  → 1 ROOM MESSAGE!      │                       │
│              └─────────────────────────┘                       │
└─────────────────────────────────────────────────────────────────┘

✅ Setiap broker saling forward message (PARALLEL)
✅ Semua app menerima semua pesan
✅ Database SQLite sinkron di semua PC
```

---

## 📁 Struktur Folder Project

```
sc_rabbitmq_sqlite_sync_app/
├── config/
│   └── network_config.json          ← MASTER CONFIG (edit ini!)
│
├── scripts/
│   ├── generate_federation.py       ← Generate RabbitMQ config
│   ├── generate_docker_compose.py   ← Generate Docker Compose
│   └── deploy.py                    ← Auto deploy script
│
├── output/
│   ├── pc1/
│   │   ├── docker-compose.yml
│   │   ├── .env
│   │   ├── federation_setup.bat
│   │   ├── verify_federation.bat
│   │   ├── start.bat
│   │   ├── stop.bat
│   │   └── README.md
│   ├── pc2/
│   └── ... (pc3-pc10)
│
├── A/                                ← App source code
│   └── sync_chatting_app.py
├── B/                                ← App source code
│   └── sync_chatting_app.py
└── Dockerfile
```

---

## 🚀 Quick Start Guide

### Step 1: Edit Konfigurasi Network

Edit file `config/network_config.json`:

```json
{
  "cluster_name": "chat_federation",
  "exchange_name": "chat_exchange",
  "rabbitmq_user": "guest",
  "rabbitmq_pass": "guest",
  "rabbitmq_port": 5672,
  "management_port": 15672,
  
  "nodes": [
    {
      "name": "pc1",
      "hostname": "pc1.local",
      "ip": "192.168.1.10",    // ← Edit sesuai IP PC Anda
      "location": "Office - Room 1",
      "enabled": true,
      "username": "user_pc1"
    },
    {
      "name": "pc2",
      "hostname": "pc2.local",
      "ip": "192.168.1.11",    // ← Edit sesuai IP PC Anda
      "location": "Office - Room 2",
      "enabled": true,
      "username": "user_pc2"
    }
    // ... tambahkan sampai pc10
  ]
}
```

**⚠️ PENTING:** Edit IP address sesuai dengan network Anda!

---

### Step 2: Generate Konfigurasi

Jalankan script generator:

```bash
cd d:\Github\sc_rabbitmq_sqlite_sync_app

# Generate RabbitMQ federation config
python scripts/generate_federation.py

# Generate Docker Compose files
python scripts/generate_docker_compose.py
```

Output akan tersimpan di folder `output/<node_name>/`

---

### Step 3: Deploy ke Setiap PC

**Opsi A: Manual Copy (Recommended)**

```bash
# Generate deployment package
python scripts/deploy.py --method manual
```

Folder `deployment_package` akan dibuat. Copy folder ini ke USB drive atau network share, lalu distribusikan ke setiap PC.

**Opsi B: SCP (Linux/WSL)**

```bash
python scripts/deploy.py --method scp --user admin --password secret
```

---

### Step 4: Setup di Setiap PC

**Di PC 1 (192.168.1.10):**

1. Copy folder `pc1` dari deployment package ke PC
2. Buka Command Prompt **sebagai Administrator**
3. Jalankan:

```batch
cd pc1
federation_setup.bat
```

4. Tunggu setup selesai
5. Jalankan:

```batch
start.bat
```

**Di PC 2 (192.168.1.11):**

1. Copy folder `pc2` dari deployment package ke PC
2. Buka Command Prompt **sebagai Administrator**
3. Jalankan:

```batch
cd pc2
federation_setup.bat
start.bat
```

**Ulangi untuk PC 3-10!**

---

### Step 5: Verifikasi

**Test 1: Cek RabbitMQ Federation**

Di setiap PC, jalankan:

```batch
verify_federation.bat
```

Anda harus melihat semua upstream nodes terdaftar.

**Test 2: Chat Test**

**Terminal 1 - PC 1:**

```batch
docker exec -it chat_app_pc1 python sync_chatting_app.py
# Masukkan username: user_a
```

**Terminal 2 - PC 2:**

```batch
docker exec -it chat_app_pc2 python sync_chatting_app.py
# Masukkan username: user_b
```

**Test 3: Kirim Pesan**

Ketik pesan di PC 1 → harus muncul di PC 2!
Ketik pesan di PC 2 → harus muncul di PC 1!

---

## 📊 Konfigurasi Detail

### Network Configuration

| Parameter | Default | Keterangan |
|-----------|---------|------------|
| `rabbitmq_port` | 5672 | Port AMQP untuk komunikasi RabbitMQ |
| `management_port` | 15672 | Port untuk RabbitMQ Management UI |
| `exchange_name` | chat_exchange | Nama exchange untuk federation |
| `cluster_name` | chat_federation | Nama cluster federation |

### Federation Configuration

| Parameter | Default | Keterangan |
|-----------|---------|------------|
| `ack_mode` | on-confirm | Acknowledge mode untuk reliability |
| `max_hops` | 1 | Maximum hops untuk message forwarding |
| `prefetch_count` | 100 | Number of messages to prefetch |

### Node Configuration

Setiap node harus punya:

| Field | Required | Contoh |
|-------|----------|--------|
| `name` | ✅ | pc1 |
| `hostname` | ✅ | pc1.local |
| `ip` | ✅ | 192.168.1.10 |
| `location` | ✅ | Office - Room 1 |
| `enabled` | ✅ | true |
| `username` | ⚠️ | user_pc1 (opsional) |

---

## 🔧 Troubleshooting

### Problem: "rabbitmqctl not found"

**Solusi:**
```
1. Install RabbitMQ: https://rabbitmq.com/install-windows.html
2. Restart Command Prompt
3. Jalankan ulang federation_setup.bat
```

### Problem: "Docker is not running"

**Solusi:**
```
1. Buka Docker Desktop
2. Tunggu status "Running"
3. Jalankan ulang start.bat
```

### Problem: "Upstream connection failed"

**Solusi:**
```
1. Pastikan semua PC bisa saling ping
2. Cek firewall - port 5672 harus terbuka
3. Verifikasi IP address di network_config.json
```

**Test koneksi:**
```batch
ping 192.168.1.11
telnet 192.168.1.11 5672
```

### Problem: "Pesan tidak muncul di PC lain"

**Solusi:**
```
1. Verifikasi federation: verify_federation.bat
2. Cek log RabbitMQ: docker-compose logs rabbitmq
3. Pastikan exchange name sama di semua PC
```

### Problem: "Database tidak sinkron"

**Solusi:**
```
1. Restart semua containers: docker-compose restart
2. Clear database dan test ulang: del chat.db
3. Jalankan ulang app: docker-compose up -d
```

---

## 📝 File Configuration

### network_config.json (Master Config)

File utama yang berisi konfigurasi semua node. Edit file ini sebelum generate.

**Lokasi:** `config/network_config.json`

**Field penting:**
- `cluster_name`: Nama cluster federation
- `exchange_name`: Nama exchange untuk broadcast
- `nodes[]`: Array berisi semua node dalam cluster

### docker-compose.yml (Auto-generated)

File Docker Compose untuk setiap node. **Jangan edit manual!** Generate dari script.

**Lokasi:** `output/<node_name>/docker-compose.yml`

**Services:**
- `rabbitmq`: RabbitMQ broker dengan federation plugin
- `chat_app`: Aplikasi chat Python

### .env (Auto-generated)

Environment variables untuk Docker Compose.

**Lokasi:** `output/<node_name>/.env`

**Variables:**
- `NODE_NAME`: Nama node
- `NODE_IP`: IP address node
- `RABBITMQ_HOST`: Host RabbitMQ (localhost untuk federation)
- `EXCHANGE_NAME`: Nama exchange

### federation_setup.bat (Auto-generated)

Script untuk setup RabbitMQ federation di setiap PC.

**Lokasi:** `output/<node_name>/federation_setup.bat`

**Actions:**
1. Enable federation plugin
2. Setup upstream ke semua node lain
3. Setup federation exchange

---

## 🔐 Security Considerations

### Production Checklist

- [ ] Ganti default credentials (`guest/guest`)
- [ ] Enable TLS/SSL untuk komunikasi RabbitMQ
- [ ] Setup firewall rules (hanya port yang diperlukan)
- [ ] Gunakan network segment terpisah untuk RabbitMQ traffic
- [ ] Enable audit logging
- [ ] Setup monitoring dan alerting

### Firewall Rules

**Port yang harus dibuka:**

| Port | Protocol | Purpose | Direction |
|------|----------|---------|-----------|
| 5672 | TCP | AMQP | Inbound/Outbound |
| 15672 | TCP | Management UI | Inbound (admin only) |

**Windows Firewall Command:**
```batch
netsh advfirewall firewall add rule name="RabbitMQ AMQP" dir=in action=allow protocol=TCP localport=5672
netsh advfirewall firewall add rule name="RabbitMQ Management" dir=in action=allow protocol=TCP localport=15672
```

---

## 📈 Monitoring & Maintenance

### RabbitMQ Management UI

**Akses:** `http://<ip-pc>:15672`

**Credentials:** `guest/guest` (default)

**Monitoring:**
- Connections: Jumlah client yang connect
- Channels: Jumlah channel aktif
- Exchanges: Status exchange federation
- Queues: Jumlah pesan antri
- Federation: Status upstream/downstream

### View Logs

**Semua logs:**
```batch
docker-compose logs -f
```

**RabbitMQ logs only:**
```batch
docker-compose logs -f rabbitmq
```

**Chat app logs only:**
```batch
docker-compose logs -f chat_app
```

### Backup Database

**Backup chat.db:**
```batch
docker cp chat_app_pc1:/app/chat.db chat.db.backup
```

**Restore chat.db:**
```batch
docker cp chat.db.backup chat_app_pc1:/app/chat.db
docker-compose restart chat_app
```

---

## 🎯 Performance Tuning

### Recommended Settings untuk 10 PC

```json
{
  "federation": {
    "ack_mode": "on-confirm",
    "max_hops": 1,
    "prefetch_count": 100
  }
}
```

**Penjelasan:**
- `ack_mode: on-confirm` → Message tidak hilang jika network down
- `max_hops: 1` → Message tidak forward berantai (mencegah loop)
- `prefetch_count: 100` → Buffer message untuk performance

### Network Requirements

| Parameter | Minimum | Recommended |
|-----------|---------|-------------|
| Bandwidth | 1 Mbps | 10 Mbps |
| Latency | < 100ms | < 10ms |
| Packet Loss | < 1% | 0% |

---

## 📚 Reference

### RabbitMQ Federation Documentation

- Official Docs: https://www.rabbitmq.com/federation.html
- Federation Tutorial: https://www.rabbitmq.com/federation-tutorial.html

### Related Projects

- RabbitMQ Clustering: https://www.rabbitmq.com/clustering.html
- RabbitMQ High Availability: https://www.rabbitmq.com/ha.html

---

## 💡 FAQ

### Q: Apakah semua PC harus 1 LAN?

**A:** Tidak harus. Federation bisa bekerja via WAN/Internet asalkan:
- Semua PC bisa saling connect via network
- Port 5672 terbuka di firewall
- Latency tidak terlalu tinggi (< 500ms)

### Q: Apa yang terjadi jika 1 PC mati?

**A:** PC lain tetap bisa chat! Federation bersifat decentralized. Tidak ada single point of failure.

### Q: Berapa delay sinkronisasi?

**A:** Biasanya < 100ms untuk LAN, tergantung:
- Network latency
- Message size
- Federation configuration

### Q: Apakah database bisa benar-benar sinkron 100%?

**A:** Ya, dengan konsep **Eventual Consistency**. Semua database akan sama "pada akhirnya", tapi mungkin ada delay beberapa milidetik.

### Q: Bagaimana cara menambah PC baru?

**A:**
1. Edit `network_config.json` - tambahkan node baru
2. Run `python scripts/generate_federation.py`
3. Run `python scripts/generate_docker_compose.py`
4. Copy folder node baru ke PC yang bersangkutan
5. Jalankan `federation_setup.bat` dan `start.bat`

---

## 📞 Support

Untuk pertanyaan atau issue, silakan:
1. Cek troubleshooting section di atas
2. Lihat log dengan `docker-compose logs -f`
3. Verifikasi federation dengan `verify_federation.bat`

---

**Version:** 1.0.0  
**Last Updated:** 2026-03-19  
**Author:** RabbitMQ Federation Chat App Team
