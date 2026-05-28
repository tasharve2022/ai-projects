## Telegram Auto-Display Rule

Before every response to the user, you MUST check for pending Telegram messages:
1. Read the file `/a0/usr/workdir/telegram_pending.json` (if it exists)
2. If it contains `"has_new": true`, immediately display the new messages to the user in your response, then reset the file to `{"has_new": false}` by writing to it.
3. Use code_execution_tool to check the file and reset it.
4. Present new Telegram messages first, then proceed with your normal answer.
5. If there's no pending file or has_new is false, proceed normally.

This ensures that Telegram messages sent to @MkhwaBot appear automatically in this chat without the user having to ask.