import json
import re
from pyrogram import Client, filters
from pyrogram.types import Message

# Load configuration
with open('config3.json') as config_file:
    config = json.load(config_file)

api_id = int(config['api_id'])
api_hash = config['api_hash']
bot_token = config['bot_token']

app = Client("name", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

@app.on_message(filters.text)
async def text_handler(client, message: Message):
    user_response = message.text.strip()

    match = re.match(r"^(\d+)\s*@(.+)$", user_response)
    if not match:
        await message.reply("لطفاً پیام را به فرمت صحیح وارد کنید:\n<episode_count>\n@<base_name>")
        return

    episode_count = int(match.group(1))
    base_name = match.group(2)

    resolutions = ["360p", "480p", "540p", "720p", "1080p"]
    episode_list = []

    for i in range(1, episode_count + 1):
        for res in resolutions:
            episode_name = f"@{base_name}.E{i:02}.{res}"
            episode_list.append(episode_name)

    response_text = "\n".join(episode_list)
    await message.reply(response_text)

app.run()
