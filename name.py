import json
from pyrogram import Client, filters
from pyrogram.types import Message

# Load configuration
with open('config3.json') as config_file:
    config = json.load(config_file)

api_id = int(config['api_id'])
api_hash = config['api_hash']
bot_token = config['bot_token']

app = Client("name", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Dictionary to store user state
user_data = {}

@app.on_message(filters.text)
async def text_handler(client, message: Message):
    user_id = message.from_user.id
    user_response = message.text

    # Initialize user data if not set
    if user_id not in user_data:
        user_data[user_id] = {"step": "episode_count"}

    # Check current step
    current_step = user_data[user_id].get("step")

    if current_step == "episode_count":
        if user_response.isdigit():
            user_data[user_id]["episode_count"] = int(user_response)
            user_data[user_id]["step"] = "get_name"
            await message.reply("اسم رو به من بگو")
        else:
            await message.reply("لطفاً یک عدد وارد کنید.")

    elif current_step == "get_name":
        base_name = user_response
        episode_count = user_data[user_id]["episode_count"]
        user_data.pop(user_id)  # Clear data after use

        resolutions = ["360p", "480p", "540p", "720p", "1080p"]
        episode_list = []

        for i in range(1, episode_count + 1):
            for res in resolutions:
                episode_name = f"{base_name}.E{i:02}.{res}"
                await message.reply(f'```{episode_name}```')

        await message.reply("شروع مجدد /start")

app.run()
