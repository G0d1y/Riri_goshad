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
        user_data[user_id] = {}

    # Check if user has already provided episode count
    if "episode_count" not in user_data[user_id]:
        # Expecting episode count as a number
        if user_response.isdigit():
            user_data[user_id]["episode_count"] = int(user_response)
            await message.reply("لطفاً نام را وارد کنید")
        else:
            await message.reply("لطفاً یک عدد معتبر وارد کنید.")
    
    elif "base_name" not in user_data[user_id]:
        # Expecting the base name after episode count
        user_data[user_id]["base_name"] = user_response
        episode_count = user_data[user_id]["episode_count"]
        base_name = user_data[user_id]["base_name"]

        # Generate the episode list
        resolutions = ["360p", "480p", "540p", "720p", "1080p"]

        for i in range(1, episode_count + 1):
            for res in resolutions:
                episode_name = f"{base_name}.E{i:02}.{res}"
                await message.reply(f'```{episode_name}```')

        await message.reply("شروع مجدد /start")

        # Clear user data for a new session
        user_data.pop(user_id)

app.run()
