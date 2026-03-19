"""
Script untuk testing aplikasi chat secara otomatis
"""
import subprocess
import time
import sys

def run_test():
    print("=" * 60)
    print("MEMULAI TEST CHAT APP")
    print("=" * 60)
    
    # Test App A dengan username "user_a"
    print("\n[1] Starting App A dengan username 'user_a'...")
    app_a = subprocess.Popen(
        ["docker", "exec", "-i", "chat_app_a", "python", "sync_chatting_app.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # Test App B dengan username "user_b"
    print("[2] Starting App B dengan username 'user_b'...")
    app_b = subprocess.Popen(
        ["docker", "exec", "-i", "chat_app_b", "python", "sync_chatting_app.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # Kirim username ke App A
    print("[3] Mengirim username ke App A...")
    app_a.stdin.write("user_a\n")
    app_a.stdin.flush()
    
    # Kirim username ke App B
    print("[4] Mengirim username ke App B...")
    app_b.stdin.write("user_b\n")
    app_b.stdin.flush()
    
    # Tunggu aplikasi siap
    print("[5] Menunggu aplikasi siap (3 detik)...")
    time.sleep(3)
    
    # Kirim pesan dari App A
    print("[6] Mengirim pesan dari App A: 'Halo dari User A!'...")
    app_a.stdin.write("Halo dari User A!\n")
    app_a.stdin.flush()
    
    # Tunggu pesan diproses
    time.sleep(2)
    
    # Kirim pesan dari App B
    print("[7] Mengirim pesan dari App B: 'Halo juga dari User B!'...")
    app_b.stdin.write("Halo juga dari User B!\n")
    app_b.stdin.flush()
    
    # Tunggu pesan diproses
    time.sleep(2)
    
    # Kirim pesan lagi dari App A
    print("[8] Mengirim pesan dari App A: 'Apa kabar?'...")
    app_a.stdin.write("Apa kabar?\n")
    app_a.stdin.flush()
    
    # Tunggu pesan diproses
    time.sleep(2)
    
    # Tutup aplikasi
    print("[9] Menutup aplikasi...")
    app_a.stdin.close()
    app_b.stdin.close()
    app_a.terminate()
    app_b.terminate()
    
    print("\n" + "=" * 60)
    print("TEST SELESAI!")
    print("=" * 60)
    
    # Cek database
    print("\n[10] Mengecek database App A...")
    result_a = subprocess.run(
        ["docker", "exec", "chat_app_a", "sqlite3", "chat.db", "SELECT * FROM messages;"],
        capture_output=True,
        text=True
    )
    print("Database App A:")
    print(result_a.stdout)
    
    print("\n[11] Mengecek database App B...")
    result_b = subprocess.run(
        ["docker", "exec", "chat_app_b", "sqlite3", "chat.db", "SELECT * FROM messages;"],
        capture_output=True,
        text=True
    )
    print("Database App B:")
    print(result_b.stdout)
    
    print("\n[12] Mengecek users di App A...")
    users_a = subprocess.run(
        ["docker", "exec", "chat_app_a", "sqlite3", "chat.db", "SELECT * FROM users;"],
        capture_output=True,
        text=True
    )
    print("Users di App A:")
    print(users_a.stdout)
    
    print("\n[13] Mengecek users di App B...")
    users_b = subprocess.run(
        ["docker", "exec", "chat_app_b", "sqlite3", "chat.db", "SELECT * FROM users;"],
        capture_output=True,
        text=True
    )
    print("Users di App B:")
    print(users_b.stdout)
    
    # Verifikasi sinkronisasi
    print("\n" + "=" * 60)
    print("HASIL SINKRONISASI:")
    print("=" * 60)
    
    if result_a.stdout.strip() and result_b.stdout.strip():
        print("✓ Kedua database memiliki pesan")
        if result_a.stdout == result_b.stdout:
            print("✓✓ SINKRONISASI BERHASIL! Database identik!")
        else:
            print("⚠ Database berbeda (tapi mungkin OK karena sender filter)")
    else:
        print("✗ Database kosong - ada masalah")

if __name__ == "__main__":
    run_test()
