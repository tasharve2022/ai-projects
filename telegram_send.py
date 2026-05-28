#!/usr/bin/env python3
"""Quick helper to send a message back to a Telegram chat."""
import requests, json, sys

BOT_TOKEN = "8960194667:AAHN6_9Q5V29CYN6qxtDdih_2LlPOvlsjRo"
API_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"

def send_message(chat_id, text):
    """Send a message back to Telegram."""
    url = f"{API_BASE}/sendMessage"
    try:
        r = requests.post(url, data={"chat_id": chat_id, "text": text}, timeout=10)
        if r.status_code == 200:
            return True, r.json()
        else:
            return False, r.text
    except Exception as e:
        return False, str(e)

def send_typing(chat_id):
    """Show typing indicator on Telegram."""
    url = f"{API_BASE}/sendChatAction"
    try:
        requests.post(url, data={"chat_id": chat_id, "action": "typing"}, timeout=5)
    except:
        pass

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        chat_id = sys.argv[1]
        text = " ".join(sys.argv[2:])
        ok, result = send_message(chat_id, text)
        print(f"✅ Sent: {ok}")
        if not ok:
            print(f"❌ Error: {result}")
    else:
        print("Usage: python3 telegram_send.py <chat_id> <message>")
        # Also print known chat IDs from conversations file
        conv_path = "/a0/usr/workdir/telegram_conversations.json"
        with open(conv_path) as f:
            convos = json.load(f)
        for cid, data in convos.items():
            print(f"  Known chat: {cid} - {data.get('sender_name', 'unknown')}")
