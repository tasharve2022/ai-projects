# Telegram Direct Reply Rule

## When processing pending Telegram messages from the bridge:
1. When I read new messages from `/a0/usr/workdir/telegram_messages.md` or find `has_new: true` in `/a0/usr/workdir/telegram_pending.json`
2. After understanding and processing the user's request
3. I MUST send my response directly to the Telegram user by using:
   ```bash
   python3 /a0/usr/workdir/telegram_send.py <chat_id> <response_text>
   ```
   Where `<chat_id>` is extracted from `telegram_conversations.json`

## Response style for Telegram:
- **Rich, structured format** with clear sections, emoji headers, and numbered lists
- Use emojis meaningfully: ✅, 🌟, 📋, 🔧, 🛡️, 🚀, 🎯, etc.
- Include detailed breakdowns with numbered benefits/features
- Use bold headings and clear visual separators (─── lines)
- NOT just 2-5 sentences - be thorough and structured when the content warrants it
- For command results: give a comprehensive but well-organized summary
- For questions: answer directly with supporting details
- For installations: confirm success + full benefits breakdown
- Match the style of detailed, professional AI analyses
- HTML/markdown formatting works in Telegram

## Example format:
```
🌟 **Package Name vX.X — Installed!**

━━━━━━━━━━━━━━━━━━

What it does: [brief description]

Key benefits:

Benefit 1 — [Title] 🎯
[Explanation with context]

Benefit 2 — [Title] 🔧
[Explanation with context]

━━━━━━━━━━━━━━━━━━

Integration: [quick setup command if applicable]
```

## Chat ID:
- @Kaylo78 (Arveson Wafula): 6219854808
- Check `telegram_conversations.json` for other users

## Note:
- Also continue to show results in this chat as normal
- The telegram_send.py script handles sending via @MkhwaBot API