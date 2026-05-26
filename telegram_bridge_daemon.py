#!/usr/bin/env python3
"""
Telegram to Agent Zero Bridge - Continuous polling daemon
"""
import requests
import json
import os
import time
import sys
from datetime import datetime, timezone

BOT_TOKEN = "8659342325:AAEaeCGi-apXb3KxHizaHpfJ5Sg-tXbiXOA"
BRIDGE_FILE = "/a0/usr/workdir/telegram_messages.md"
OFFSET_FILE = "/a0/usr/workdir/telegram_offset.txt"

API_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"

def get_updates(offset=None):
    url = f"{API_BASE}/getUpdates"
    params = {"timeout": 10}
    if offset:
        params["offset"] = offset
    try:
        r = requests.get(url, params=params, timeout=15)
        return r.json()
    except Exception as e:
        return {"ok": False, "error": str(e)}

def load_offset():
    if os.path.exists(OFFSET_FILE):
        with open(OFFSET_FILE) as f:
            try:
                return int(f.read().strip())
            except:
                return None
    return None

def save_offset(offset):
    with open(OFFSET_FILE, "w") as f:
        f.write(str(offset))

def format_message(msg):
    chat = msg.get("chat", {})
    sender = msg.get("from", {})
    username = sender.get("username", "")
    first = sender.get("first_name", "")
    last = sender.get("last_name", "")
    
    if username:
        sender_name = f"@{username}"
    elif first or last:
        sender_name = f"{first} {last}".strip()
    else:
        sender_name = str(sender.get("id", "Unknown"))
    
    text = msg.get("text") or msg.get("caption") or "[non-text message]"
    date = msg.get("date", 0)
    
    return {
        "sender": sender_name,
        "chat_id": chat.get("id"),
        "text": text,
        "timestamp": date,
        "message_id": msg.get("message_id")
    }

def append_to_file(messages):
    if not messages:
        return
    with open(BRIDGE_FILE, "a") as f:
        for msg in messages:
            ts = datetime.fromtimestamp(msg["timestamp"], tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            entry = f"### {ts} - From: {msg['sender']}\n> {msg['text']}\n\n"
            f.write(entry)
            print(f"[NEW] {ts} - {msg['sender']}: {msg['text']}")
    sys.stdout.flush()

def poll_loop():
    print("🚀 Telegram Bridge Daemon started! Polling every 5 seconds...")
    sys.stdout.flush()
    while True:
        try:
            offset = load_offset()
            result = get_updates(offset)
            
            if result.get("ok"):
                updates = result.get("result", [])
                new_messages = []
                for update in updates:
                    update_id = update.get("update_id")
                    if "message" in update:
                        msg = update["message"]
                        formatted = format_message(msg)
                        new_messages.append(formatted)
                    if update_id:
                        save_offset(update_id + 1)
                
                if new_messages:
                    append_to_file(new_messages)
        except Exception as e:
            print(f"⚠️ Error: {e}")
            sys.stdout.flush()
        
        time.sleep(5)

if __name__ == "__main__":
    poll_loop()
