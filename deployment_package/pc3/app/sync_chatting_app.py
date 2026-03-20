import pika
import sqlite3
import threading
import json
import time
import os
import sys
import configparser
from datetime import datetime

# ============================================================================
# Configuration Loading
# ============================================================================

def load_config():
    """Load configuration from environment variables or config file"""
    config = {
        'rabbitmq_host': os.environ.get('RABBITMQ_HOST', 'localhost'),
        'rabbitmq_port': int(os.environ.get('RABBITMQ_PORT', '5672')),
        'rabbitmq_user': os.environ.get('RABBITMQ_USER', 'guest'),
        'rabbitmq_pass': os.environ.get('RABBITMQ_PASS', 'guest'),
        'exchange_name': os.environ.get('EXCHANGE_NAME', 'chat_exchange'),
        'node_name': os.environ.get('NODE_NAME', 'unknown'),
        'node_ip': os.environ.get('NODE_IP', '127.0.0.1'),
        'default_username': os.environ.get('DEFAULT_USERNAME', ''),
    }
    
    # Try to load from config.ini if exists
    config_file = 'config.ini'
    if os.path.exists(config_file):
        try:
            parser = configparser.ConfigParser()
            parser.read(config_file)
            
            if 'RABBITMQ' in parser:
                config['rabbitmq_host'] = parser.get('RABBITMQ', 'host', fallback=config['rabbitmq_host'])
                config['rabbitmq_port'] = parser.getint('RABBITMQ', 'port', fallback=config['rabbitmq_port'])
                config['rabbitmq_user'] = parser.get('RABBITMQ', 'user', fallback=config['rabbitmq_user'])
                config['rabbitmq_pass'] = parser.get('RABBITMQ', 'password', fallback=config['rabbitmq_pass'])
            
            if 'FEDERATION' in parser:
                config['exchange_name'] = parser.get('FEDERATION', 'exchange', fallback=config['exchange_name'])
            
            if 'NODE' in parser:
                config['default_username'] = parser.get('NODE', 'username', fallback=config['default_username'])
        except Exception as e:
            print(f"[WARNING] Failed to load config.ini: {e}")
    
    return config

# Load configuration
print("[INFO] Loading configuration...")
config = load_config()

print(f"  - RabbitMQ Host: {config['rabbitmq_host']}")
print(f"  - RabbitMQ Port: {config['rabbitmq_port']}")
print(f"  - Exchange: {config['exchange_name']}")
print(f"  - Node: {config['node_name']} ({config['node_ip']})")
print()

# Get username from command line, config, or input
if len(sys.argv) > 1:
    USERNAME = sys.argv[1]
elif config['default_username']:
    USERNAME = config['default_username']
    print(f"[INFO] Using default username: {USERNAME}")
else:
    try:
        USERNAME = input("Masukkan username: ")
    except (EOFError, KeyboardInterrupt):
        USERNAME = f"user_{config['node_name']}"
        print(f"[INFO] Using auto-generated username: {USERNAME}")

# --- Setup SQLite ---
conn = sqlite3.connect("chat.db", check_same_thread=False)
cursor = conn.cursor()
conn_lock = threading.Lock()

# Tabel messages dengan UNIQUE constraint untuk mencegah duplikasi
cursor.execute("""CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    text TEXT,
    timestamp TEXT,
    UNIQUE(username, timestamp, text)
)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    joined_at TEXT
)""")
conn.commit()

# --- Consumer ---
def consume():
    """Consumer thread - receive messages from RabbitMQ"""
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=config['rabbitmq_host'],
                port=config['rabbitmq_port'],
                credentials=pika.PlainCredentials(
                    config['rabbitmq_user'], 
                    config['rabbitmq_pass']
                ),
                heartbeat=600
            )
        )
        channel = connection.channel()

        # Gunakan Fanout Exchange untuk broadcast
        channel.exchange_declare(
            exchange=config['exchange_name'], 
            exchange_type='fanout', 
            durable=True
        )

        # Buat queue unik untuk tiap client (auto-delete)
        result = channel.queue_declare(queue='', exclusive=True, auto_delete=True)
        queue_name = result.method.queue

        # Bind queue ke exchange
        channel.queue_bind(exchange=config['exchange_name'], queue=queue_name)

        def callback(ch, method, properties, body):
            try:
                event = json.loads(body.decode())

                if event["type"] == "message" and event["action"] == "create":
                    with conn_lock:
                        cursor.execute(
                            "INSERT OR IGNORE INTO messages (username, text, timestamp) VALUES (?, ?, ?)",
                            (event["sender"], event["text"], event["timestamp"])
                        )
                        conn.commit()
                    print(f"\n[{event['sender']}] {event['text']}")
                    print("Ketik pesan: ", end="", flush=True)

                elif event["type"] == "user" and event["action"] == "create":
                    with conn_lock:
                        cursor.execute(
                            "INSERT OR IGNORE INTO users (username, joined_at) VALUES (?, ?)",
                            (event["sender"], event["joined_at"])
                        )
                        conn.commit()
                    print(f"\n[INFO] User baru terdaftar: {event['sender']}")
            except Exception as e:
                print(f"[ERROR] Callback error: {e}")

        channel.basic_consume(
            queue=queue_name, 
            on_message_callback=callback, 
            auto_ack=True
        )
        print(" [*] Menunggu pesan...")

        # Non-blocking consume
        while True:
            try:
                channel.connection.process_data_events(time_limit=1)
            except:
                break

        connection.close()
    except Exception as e:
        print(f"[ERROR] Consumer connection failed: {e}")
        print(f"  RabbitMQ Host: {config['rabbitmq_host']}")
        print(f"  RabbitMQ Port: {config['rabbitmq_port']}")

# --- Producer ---
def produce():
    """Producer function - send messages to RabbitMQ"""
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=config['rabbitmq_host'],
                port=config['rabbitmq_port'],
                credentials=pika.PlainCredentials(
                    config['rabbitmq_user'], 
                    config['rabbitmq_pass']
                ),
                heartbeat=600
            )
        )
        channel = connection.channel()

        # Gunakan Fanout Exchange untuk broadcast
        channel.exchange_declare(
            exchange=config['exchange_name'], 
            exchange_type='fanout', 
            durable=True
        )

        # register user
        user_event = {
            "action": "create",
            "type": "user",
            "sender": USERNAME,
            "joined_at": datetime.now().isoformat()
        }
        channel.basic_publish(
            exchange=config['exchange_name'],
            routing_key='',
            body=json.dumps(user_event),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        print(f"[INFO] Registered user: {USERNAME}")

        while True:
            try:
                message = input("Ketik pesan: ")
                event = {
                    "action": "create",
                    "type": "message",
                    "sender": USERNAME,
                    "text": message,
                    "timestamp": datetime.now().isoformat()
                }
                channel.basic_publish(
                    exchange=config['exchange_name'],
                    routing_key='',
                    body=json.dumps(event),
                    properties=pika.BasicProperties(delivery_mode=2)
                )
                print(f"[x] Sent: {event}")
            except EOFError:
                break

        connection.close()
    except Exception as e:
        print(f"[ERROR] Producer connection failed: {e}")
        print(f"  RabbitMQ Host: {config['rabbitmq_host']}")
        print(f"  RabbitMQ Port: {config['rabbitmq_port']}")

# --- Run ---
print(f"\n=== Chat Client Started (User: {USERNAME}) ===")

# Start consumer thread
consumer_thread = threading.Thread(target=consume, daemon=True)
consumer_thread.start()

# Tunggu consumer siap
time.sleep(1)

# Jalankan producer
produce()
