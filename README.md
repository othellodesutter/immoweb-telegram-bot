# Immoweb Telegram bot
Telegram bot that notifies the user when a new property that corresponds to their query was added to [Immoweb](https://www.immoweb.be/en).

## Installation
The only requirement is having the *requests* library installed.

```bash
pip install requests
```

## Configuration
Make a new file in the main directory called *config.py* with the following structure:

```python
config = {
    'token': '',
    'chat_id': '',
    'url': 'for example https://www.immoweb.be/en/search-results/house/for-rent?orderBy=newest'
}
```

To add a new bot on Telegram, start a conversation with [@BotFather](https://telegram.me/BotFather) and send the message `/newbot`. Choose the desired name of how you want your notifier to be called aswell as the desired username. Copy the token and paste it in the *config.py* file. 

To obtain the *chat_id* of the chat you want your bot to be in, add your freshly created bot to a group, send a message to this group starting with `/`, go to *api.telegram.org/bot`token`/getUpdates* and there you can get the *chat_id* ([I followed this guide](https://stackoverflow.com/questions/32423837/telegram-bot-how-to-get-a-group-chat-id)). 

Go to [Immoweb](https://www.immoweb.be/en), search what you want to monitor, click on **sort by new**, copy the url and change the `/search/` to `/search-results/`. Put this *url* in the *config.py* file.

## Usage
Start the bot by running the *script.py* file.
