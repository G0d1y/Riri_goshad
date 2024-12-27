import json
import re
import os
import subprocess
import signal
import time
from pyrogram import Client, filters
from pyrogram.types import Message, InputMediaDocument
from pyrogram.types import ReplyKeyboardMarkup
from pyrogram.types import ReplyKeyboardMarkup


with open('config4.json') as config_file:
    config = json.load(config_file)

api_id = int(config['api_id'])
api_hash = config['api_hash']
bot_token = bot_token = config['bot_token']

app = Client("re-order", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

user_data = {}

def extract_series_details(file_name):
    """
    Extract series details from the file name.
    """
    pattern = r"@[\w\.]+\.([\w\.]+)\.E(\d{1,2})\.(\d{3,4}p)"
    match = re.match(pattern, file_name)

    if match:
        series_name = match.group(1).replace('.', ' ')
        episode_number = int(match.group(2))
        quality = match.group(3)
        return {
            "series_name": series_name,
            "episode_number": episode_number,
            "quality": quality
        }
    else:
        return None

def find_and_kill_bot():
    try:
        pid = int(subprocess.check_output(["pgrep", "-f", "reorder.py"]))
        os.kill(pid, signal.SIGTERM)
        print(f"Stopped bot with PID {pid}")
        time.sleep(2)
    except subprocess.CalledProcessError:
        print("Bot is not running.")

def start_bot():
    subprocess.Popen(["nohup", "python3", "reorder.py", "&"])
    print("Bot restarted.")

@app.on_message(filters.command("restart"))
def restart(client, message):
    find_and_kill_bot()
    start_bot()
    client.send_message(message.chat.id, "Bot restarted.")

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    keyboard = ReplyKeyboardMarkup(
        [
            ["🟢 شروع"],
            [ "🔴 پایان"]
        ],
        resize_keyboard=True 
    )
    await message.reply("فایل هارا بفرستید" , reply_markup=keyboard)
    user_data[message.from_user.id] = {"step": "waiting_for_files", "files": []}

@app.on_message(filters.text & filters.regex("🟢 شروع"))
async def handle_button(client, message):
    await message.reply("فایل هارا بفرستید")
    user_data[message.from_user.id] = {"step": "waiting_for_files", "files": []}


@app.on_message(filters.text & filters.regex("🔴 پایان"))
async def end_command(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id in user_data and user_data[user_id]["step"] == "waiting_for_files":
        data = user_data[user_id]
        files = data["files"]

        arranged_files = {}
        
        for file_data in files:
            file_message = file_data["message"]
            file_name = file_message.document.file_name
            caption = file_message.caption  
            details = extract_series_details(file_name)
            
            if not details:
                await message.reply(f"نام فایل غیرقابل تشخیص است: {file_name}")
                continue

            series_name = details["series_name"]
            episode_number = details["episode_number"]
            quality = details["quality"]

            if series_name not in arranged_files:
                arranged_files[series_name] = {}

            if episode_number not in arranged_files[series_name]:
                arranged_files[series_name][episode_number] = {}

            arranged_files[series_name][episode_number][quality] = {"file": file_message, "caption": caption}

        
        qualities = ["360p", "480p", "540p", "720p", "1080p"]
        
        for series_name, episodes in arranged_files.items():
            for episode_number in sorted(episodes.keys()):
                media_group = []
                for quality in qualities:
                    file_entry = episodes[episode_number].get(quality)
                    if file_entry:
                        media_group.append(
                            InputMediaDocument(
                                file_entry["file"].document.file_id,
                                caption=file_entry["caption"] or file_entry["file"].document.file_name
                            )
                        )

                if media_group:
                    await client.send_media_group(message.chat.id, media_group)

        await message.reply("تمام فایل‌ها با موفقیت ارسال شدند.")
        user_data.pop(user_id, None)

@app.on_message((filters.document | filters.video) & filters.private)
async def handle_files(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id in user_data and user_data[user_id]["step"] == "waiting_for_files":
        file_name = message.document.file_name
        details = extract_series_details(file_name)

        if details:
            user_data[user_id]["files"].append({
                "message": message,
                "series_name": details["series_name"],
                "episode_number": details["episode_number"],
                "quality": details["quality"]
            })
            file_count = len(user_data[user_id]["files"])
            await message.reply(f"فایل شماره {file_count} ذخیره شد: {details['series_name']} - قسمت {details['episode_number']} - کیفیت {details['quality']}")
        else:
            await message.reply("نام فایل غیرقابل تشخیص است. لطفاً قالب فایل را بررسی کنید.")

        await client.delete_messages(user_id, message.id)
app.run()
