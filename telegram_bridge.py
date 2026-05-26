#!/usr/bin/env python3
"""
Telegram to Agent Zero Bridge - Polls for new messages and saves to a file.
"""
import requests
import json
import os
import time

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
    """Format a Telegram message nicely."""
    chat = msg.get("chat", {})
    sender = msg.get("from", {})
    chat_type = chat.get("type", "unknown")
    
    # Determine sender name
    first = sender.get("first_name", "")
    last = sender.get("last_name", "")
    username = sender.get("username", "")
    
    if username:
        sender_name = f"@{username}"
    elif first or last:
        sender_name = f"{first} {last}".strip()
    else:
        sender_name = str(sender.get("id", "Unknown"))
    
    # Get text or caption
    text = msg.get("text") or msg.get("caption") or "[non-text message]"
    date = msg.get("date", 0)
    
    return {
        "sender": sender_name,
        "chat_id": chat.get("id"),
        "text": text,
        "timestamp": date,
        "message_id": msg.get("message_id")
    }

def poll():
    offset = load_offset()
    result = get_updates(offset)
    
    if not result.get("ok"):
        return []
    
    updates = result.get("result", [])
    new_messages = []
    
    for update in updates:
        update_id = update.get("update_id")
        if "message" in update:
            msg = update["message"]
            formatted = format_message(msg)
            new_messages.append(formatted)
        # Update offset to the next update_id
        if update_id:
            save_offset(update_id + 1)
    
    return new_messages

def append_to_file(messages):
    """Append new messages to the bridge file."""
    if not messages:
        return
    
    with open(BRIDGE_FILE, "a") as f:
        for msg in messages:
            from datetime import datetime
            ts = datetime.utcfromtimestamp(msg["timestamp"]).strftime("%Y-%m-%d %H:%M:%S UTC")
            f.write(f"### {ts} - From: {msg['sender']}\n")
            f.write(f"> {msg['text']}\n\n")

if __name__ == "__main__":
    from datetime import datetime
    new_msgs = poll()
    if new_msgs:
        append_to_file(new_msgs)
        print(f"📩 {len(new_msgs)} new message(s) received")
        for msg in new_msgs:
            ts = datetime.utcfromtimestamp(msg["timestamp"]).strftime("%H:%M:%S")
            print(f"  [{ts}] {msg['sender']}: {msg['text']}")
    else:
        print("No new messages.")
