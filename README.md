# Gmail-to-Discord-Notifier
A personal project. I don't always have a browser or my Gmail open, but Discord is always running in the background. So I built this tool to forward my new unread Gmail subjects and snippets into a Discord channel. I won't miss any important email, even if Gmail is closed.

This project uses Google's official Python libraries for Gmail API, plus Discord webhooks for the notifications. The heavy lifting is done by Google's prewritten tools, I just tied everything together.

## How It Works
- Authenticates with Gmail via OAuth (using credentials.json & token.json).
- Checks my Gmail every 60 seconds for unread messages.
- Sends the subject + snippet of each new email into my Discord channel via a webhook.
- Keeps track of sent emails in sent_ids.json, so no duplicates are posted.

## Setup Instructions
1. Clone this repo.
2. Install dependencies:
```
pip install -r requirements.txt
```
3. Create a .env file with your Discord webhook URL:
```env
DISCORD_WEBHOOK=your_webhook_here
```
4. Add your Gmail API credentials.json (from Google Cloud).
5. Run the script:
```
python discord_email_notifier.py
```

## Future Improvements
This project still has room to grow:
- Better error handling. (currently, a simple network drop will crash the script).
- Email body previews, instead of just snippets.
- Run as background service instead of a manual script.


