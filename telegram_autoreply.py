#!/usr/bin/env python3
"""
Telegram AI Auto-Reply Daemon
Polls @MloshBot every 5 seconds, generates intelligent replies via DeepSeek API,
and sends them back to the user on Telegram.
"""
import requests
import json
import os
import sys
import time
from datetime import datetime, timezone

# ==================== CONFIGURATION ====================
BOT_TOKEN = "8659342325:AAEaeCGi-apXb3KxHizaHpfJ5Sg-tXbiXOA"
DEEPSEEK_KEY = os.environ.get("API_KEY_DEEPSEEK", "sk-e4fb4154ebdf49c89dea3ead1f1706e5")
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-v4-flash"

BRIDGE_FILE = "/a0/usr/workdir/telegram_messages.md"
OFFSET_FILE = "/a0/usr/workdir/telegram_offset.txt"
CONVERSATIONS_FILE = "/a0/usr/workdir/telegram_conversations.json"

API_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"

# ==================== CONVERSATION CONTEXT ====================
MAX_HISTORY = 10  # Keep last 10 messages per user for context

def load_conversations():
    if os.path.exists(CONVERSATIONS_FILE):
        try:
            with open(CONVERSATIONS_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, Exception):
            pass
    return {}

def save_conversations(convos):
    with open(CONVERSATIONS_FILE, "w") as f:
        json.dump(convos, f, indent=2, ensure_ascii=False)

def update_conversation(chat_id, role, text, sender_name):
    """Add a message to conversation history."""
    convos = load_conversations()
    key = str(chat_id)
    if key not in convos:
        convos[key] = {
            "sender_name": sender_name,
            "messages": []
        }
    convos[key]["sender_name"] = sender_name
    convos[key]["messages"].append({
        "role": role,
        "content": text,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    # Keep only last MAX_HISTORY*2 messages
    if len(convos[key]["messages"]) > MAX_HISTORY * 2:
        convos[key]["messages"] = convos[key]["messages"][-MAX_HISTORY*2:]
    save_conversations(convos)

# ==================== DEEPSEEK AI REPLY ====================
SYSTEM_PROMPT = """You are a helpful AI assistant named ZeroVPS running on the @MloshBot Telegram bot. 
You are friendly, helpful, and concise. Respond naturally to the user's messages. 
Keep responses informative but not overly long. Use a warm, conversational tone."""

def generate_reply(chat_id, user_message, sender_name):
    """Generate an intelligent reply using DeepSeek API with conversation context."""
    convos = load_conversations()
    key = str(chat_id)
    
    # Build messages array with system prompt and conversation history
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Add conversation history
    if key in convos:
        for msg in convos[key]["messages"][-MAX_HISTORY:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
    
    # Add the new user message if not already in history
    messages.append({"role": "user", "content": user_message})
    
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": DEEPSEEK_MODEL,
        "messages": messages,
        "max_tokens": 300,
        "temperature": 0.7
    }
    
    try:
        r = requests.post(DEEPSEEK_URL, headers=headers, json=data, timeout=30)
        if r.status_code == 200:
            result = r.json()
            reply = result["choices"][0]["message"]["content"].strip()
            return reply
        else:
            print(f"⚠️ DeepSeek API error: {r.status_code} - {r.text[:100]}")
            sys.stdout.flush()
            return None
    except Exception as e:
        print(f"⚠️ DeepSeek request failed: {e}")
        sys.stdout.flush()
        return None

def send_message(chat_id, text):
    """Send a message back to Telegram."""
    url = f"{API_BASE}/sendMessage"
    try:
        r = requests.post(url, data={"chat_id": chat_id, "text": text}, timeout=10)
        return r.status_code == 200
    except Exception as e:
        print(f"⚠️ Failed to send message: {e}")
        sys.stdout.flush()
        return False

def send_typing(chat_id):
    """Show typing indicator on Telegram."""
    url = f"{API_BASE}/sendChatAction"
    try:
        requests.post(url, data={"chat_id": chat_id, "action": "typing"}, timeout=5)
    except:
        pass

# ==================== TELEGRAM POLLING ====================
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
        try:
            with open(OFFSET_FILE) as f:
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

def process_and_reply():
    """Main loop: poll, process, reply."""
    print("🚀 Telegram AI Auto-Reply Daemon started!")
    print(f"🤖 Bot: @MloshBot (ZeroVPS)")
    print(f"🧠 AI: DeepSeek ({DEEPSEEK_MODEL})")
    print(f"⏱  Polling every 5 seconds...")
    sys.stdout.flush()
    
    while True:
        try:
            offset = load_offset()
            result = get_updates(offset)
            
            if result.get("ok"):
                updates = result.get("result", [])
                for update in updates:
                    update_id = update.get("update_id")
                    if "message" in update:
                        msg = update["message"]
                        formatted = format_message(msg)
                        
                        # Skip messages from the bot itself
                        if msg.get("from", {}).get("is_bot", False):
                            if update_id:
                                save_offset(update_id + 1)
                            continue
                        
                        # Skip /start command
                        if formatted["text"].startswith("/start"):
                            # Still save to file and update conversation
                            append_to_file([formatted])
                            if update_id:
                                save_offset(update_id + 1)
                            continue
                        
                        print(f"📩 {formatted['sender']}: {formatted['text']}")
                        sys.stdout.flush()
                        
                        # Save to bridge file
                        append_to_file([formatted])
                        
                        # Update conversation history with user message
                        update_conversation(
                            formatted["chat_id"],
                            "user",
                            formatted["text"],
                            formatted["sender"]
                        )
                        
                        # Show typing indicator
                        send_typing(formatted["chat_id"])
                        time.sleep(1)  # Brief pause so user sees typing
                        
                        # Generate AI reply
                        print(f"🤔 Generating reply...")
                        sys.stdout.flush()
                        reply = generate_reply(
                            formatted["chat_id"],
                            formatted["text"],
                            formatted["sender"]
                        )
                        
                        if reply:
                            # Send reply
                            success = send_message(formatted["chat_id"], reply)
                            if success:
                                print(f"✅ Replied: {reply[:80]}...")
                                # Update conversation history with assistant reply
                                update_conversation(
                                    formatted["chat_id"],
                                    "assistant",
                                    reply,
                                    "ZeroVPS Bot"
                                )
                                # Also append reply to bridge file
                                ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                                with open(BRIDGE_FILE, "a") as f:
                                    f.write(f"🤖 [{ts}] Bot replied: {reply}\n\n")
                            else:
                                print(f"❌ Failed to send reply")
                        else:
                            # Fallback reply
                            fallback = "Hi! I received your message but I'm having trouble thinking right now. Please try again!"
                            send_message(formatted["chat_id"], fallback)
                            print(f"⚠️ Sent fallback reply")
                        
                        sys.stdout.flush()
                    
                    # Always update offset
                    if update_id:
                        save_offset(update_id + 1)
            
        except KeyboardInterrupt:
            print("\n🛑 Daemon stopped by user.")
            sys.stdout.flush()
            break
        except Exception as e:
            print(f"⚠️ Error in main loop: {e}")
            sys.stdout.flush()
        
        time.sleep(5)

if __name__ == "__main__":
    process_and_reply()
