import json
import re
from pyrogram import Client, filters 
from pyrogram.types import Message 

with open('config.json') as config_file:
    config = json.load(config_file)

api_id = int(config['api_id'])
api_hash = config['api_hash']
bot_token = config['bot_token']

app = Client("bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

url_pattern = re.compile(r'https?://[^\s]+')

@app.on_message(filters.text)
def handle_message(client: Client, message: Message):
    urls = url_pattern.findall(message.text)
    
    if urls:
        for url in urls:
            client.send_message(
                chat_id=message.chat.id,
                text=f"`{url}`"
            )

app.run()
