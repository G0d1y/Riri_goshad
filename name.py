import json
from pyrogram import Client, filters
from pyrogram.types import Message

with open('config3.json') as config_file:
    config = json.load(config_file)

api_id = int(config['api_id'])
api_hash = config['api_hash']
bot_token = config['bot_token']

app = Client("name", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

user_data = {}

@app.on_message(filters.command("start"))
async def start_handler(client, message: Message):
    user_id = message.from_user.id
    await message.reply("چند قسمته؟")
    user_data[user_id] = {"step": "episode_count"}

@app.on_message(filters.text)
async def text_handler(client, message: Message):
    user_id = message.from_user.id
    user_response = message.text

    if user_id not in user_data:
        await message.reply("/start.")
        return

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
        user_data.pop(user_id)

        resolutions = ["360p", "480p", "540p", "720p", "1080p"]
        episode_list = []

        for i in range(1, episode_count + 1):
            for res in resolutions:
                episode_name = f"{base_name}.E{i:02}.{res}"
                episode_list.append(episode_name)

        response_text = "\n".join(episode_list)
        await message.reply(response_text)

app.run()
