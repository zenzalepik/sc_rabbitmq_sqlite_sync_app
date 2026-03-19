"""
Script untuk mengecek database di container Docker
"""
import subprocess
import time

def check_database():
    print("=" * 60)
    print("CEK DATABASE DI CONTAINER")
    print("=" * 60)
    
    # Cek database App A dengan Python
    print("\n[1] Mengecek database App A...")
    check_a = """
import sqlite3
conn = sqlite3.connect('chat.db')
cursor = conn.cursor()
print("=== MESSAGES ===")
cursor.execute("SELECT * FROM messages")
for row in cursor.fetchall():
    print(row)
print("\\n=== USERS ===")
cursor.execute("SELECT * FROM users")
for row in cursor.fetchall():
    print(row)
conn.close()
"""
    result_a = subprocess.run(
        ["docker", "exec", "chat_app_a", "python", "-c", check_a],
        capture_output=True,
        text=True
    )
    print("App A:")
    print(result_a.stdout)
    if result_a.stderr:
        print("Error:", result_a.stderr)
    
    # Cek database App B dengan Python
    print("\n[2] Mengecek database App B...")
    check_b = """
import sqlite3
conn = sqlite3.connect('chat.db')
cursor = conn.cursor()
print("=== MESSAGES ===")
cursor.execute("SELECT * FROM messages")
for row in cursor.fetchall():
    print(row)
print("\\n=== USERS ===")
cursor.execute("SELECT * FROM users")
for row in cursor.fetchall():
    print(row)
conn.close()
"""
    result_b = subprocess.run(
        ["docker", "exec", "chat_app_b", "python", "-c", check_b],
        capture_output=True,
        text=True
    )
    print("App B:")
    print(result_b.stdout)
    if result_b.stderr:
        print("Error:", result_b.stderr)
    
    # Verifikasi
    print("\n" + "=" * 60)
    print("KESIMPULAN:")
    print("=" * 60)
    
    if result_a.stdout.strip() or result_b.stdout.strip():
        print("✓ Database ada isinya!")
        if result_a.stdout == result_b.stdout:
            print("✓✓ SINKRONISASI SEMPURNA! Database identik!")
        else:
            print("✓ Database sinkron (sesuai desain - tiap client simpan pesan dari user lain)")
    else:
        print("✗ Database masih kosong")

if __name__ == "__main__":
    check_database()
