# 🚀 QUICK START - RabbitMQ Federation Chat App

## ⚡ Setup Cepat (5 Menit)

### Untuk 10 PC Federation Setup

---

## ⚠️ BINGUNG PILIH YANG MANA?

**Baca tabel ini dulu!**

| Fitur | Single-PC Testing | Multi-PC Federation |
|-------|------------------|---------------------|
| **Untuk apa?** | Testing/Development di 1 laptop | Production di 10 PC fisik |
| **Jumlah PC** | 1 PC | 10 PC berbeda |
| **RabbitMQ** | Di Docker (otomatis) | Install manual di Windows (tiap PC) |
| **Set IP Address** | ❌ **TIDAK PERLU** | ✅ **WAJIB EDIT DI JSON** |
| **Setup Time** | 1 menit | 30 menit |
| **File Config** | `docker-compose.yml` | `config/network_config.json` |
| **Commands** | `start.bat` | Generate + Deploy + Setup |
| **Use Case** | Belajar, testing, demo | Production kantor |

**👉 Mau testing sendiri (2 apps)?** Lihat: **[README_DOCKER.md](README_DOCKER.md)**

**👉 Mau deploy 10 PC?** Lanjut baca guide ini!

---

## 📋 Prerequisites

- ✅ Windows 10/11 Pro atau Enterprise
- ✅ Docker Desktop installed dan running
- ✅ Python 3.11+ (untuk generate config)
- ✅ RabbitMQ installed (untuk federation setup)
- ✅ 10 PC dalam 1 network (bisa saling ping)

---

## 🔧 Step-by-Step

### **STEP 1: Edit Network Config** (3 menit)

Edit file: `config/network_config.json`

```bash
notepad config\network_config.json
```

**Ganti IP address** sesuai network Anda:

```json
{
  "nodes": [
    {"name": "pc1", "ip": "192.168.1.10", "location": "Ruang 1"},
    {"name": "pc2", "ip": "192.168.1.11", "location": "Ruang 2"},
    {"name": "pc3", "ip": "192.168.1.12", "location": "Ruang 3"},
    // ... sampai pc10
  ]
}
```

**⚠️ PENTING:** 
- Semua IP harus **unik**
- Semua PC harus **1 network** (bisa saling ping)
- Port **5672** harus terbuka di firewall

---

### **STEP 2: Generate Config** (1 menit)

```bash
cd d:\Github\sc_rabbitmq_sqlite_sync_app

# Generate semua config
python scripts/generate_federation.py
python scripts/generate_docker_compose.py
python scripts/deploy.py --method manual
```

✅ Output tersimpan di folder `deployment_package/`

---

### **STEP 3: Deploy ke Setiap PC** (1 menit)

1. **Copy folder** `deployment_package` ke USB drive atau network share
2. **Distribusikan** ke setiap PC

---

### **STEP 4: Setup di Setiap PC** (1 menit per PC)

**Di PC 1:**

```batch
# 1. Copy folder pc1 ke PC
cd deployment_package\pc1

# 2. Run sebagai Administrator
federation_setup.bat

# 3. Start Docker
start.bat

# 4. Test chat
docker exec -it chat_app_pc1 python sync_chatting_app.py user_a
```

**Di PC 2:**

```batch
# 1. Copy folder pc2 ke PC
cd deployment_package\pc2

# 2. Run sebagai Administrator
federation_setup.bat

# 3. Start Docker
start.bat

# 4. Test chat
docker exec -it chat_app_pc2 python sync_chatting_app.py user_b
```

**Ulangi untuk PC 3-10!**

---

## ✅ Verifikasi

### Test 1: Kirim Pesan

**Di PC 1:**
```
Ketik: "Halo dari PC 1"
```

**Di PC 2:**
```
Harus muncul: "[user_a] Halo dari PC 1"
```

**Di PC 3-10:**
```
Harus muncul juga!
```

### Test 2: Cek Federation

Di setiap PC:
```batch
verify_federation.bat
```

Harus menampilkan **9 upstreams** (semua PC lain).

### Test 3: RabbitMQ UI

Buka browser:
```
http://<ip-pc>:15672
Username: guest
Password: guest
```

Cek **Federation** di menu - harus ada upstream dari semua PC.

---

## 🛑 Stop/Start Ulang

### Stop:
```batch
stop.bat
```

### Start:
```batch
start.bat
```

### View Logs:
```batch
docker-compose logs -f
```

---

## ❓ Troubleshooting Cepat

| Problem | Solusi |
|---------|--------|
| **"Docker is not running"** | Start Docker Desktop |
| **"rabbitmqctl not found"** | Install RabbitMQ: https://rabbitmq.com/install-windows.html |
| **"Connection refused"** | Cek firewall - buka port 5672 |
| **"Request timed out"** | Pastikan semua PC bisa saling ping |
| **Pesan tidak muncul** | Run `verify_federation.bat` - cek upstreams |

---

## 📚 Dokumentasi Lengkap

- **README_FEDERATION.md** - Guide lengkap federation setup
- **README_DOCKER.md** - Docker setup guide
- **ARSITEKTUR.md** - Arsitektur sistem

---

## 🎯 Next Steps

Setelah setup berhasil:

1. ✅ **Production Setup:**
   - Ganti default credentials (guest/guest)
   - Enable TLS/SSL
   - Setup monitoring

2. ✅ **Maintenance:**
   - Backup database: `docker cp chat_app_pc1:/app/chat.db backup.db`
   - Monitor logs: `docker-compose logs -f`
   - Check RabbitMQ UI: http://<ip-pc>:15672

3. ✅ **Scaling:**
   - Tambah PC? Edit JSON → regenerate → deploy
   - Remove PC? Set `"enabled": false` di JSON

---

**🎉 SELAMAT! Federation chat app Anda sudah jalan!**

Untuk bantuan lebih lanjut, baca **README_FEDERATION.md**
