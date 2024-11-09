import json
import re
from pyrogram import Client, filters
from pyrogram.types import Message

# Load config file
with open('config4.json') as config_file:
    config = json.load(config_file)

api_id = int(config['api_id'])
api_hash = config['api_hash']
bot_token = config['bot_token']

# Initialize bot
app = Client("cap", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Dictionary to store user data
user_data = {}

# Command /start handler
@app.on_message(filters.command("start") & filters.private)
async def start(client: Client, message: Message):
    await message.reply("تعداد قسمت‌ها و نام سریال را به فرمت زیر وارد کنید:\n\n10\n🎬 سریال آقای پلانکتون")
    user_data[message.from_user.id] = {"step": "waiting_for_info"}

# Handle text messages for episode count and series name
@app.on_message(filters.text & filters.private)
async def handle_text(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id in user_data and user_data[user_id]["step"] == "waiting_for_info":
        text = message.text.strip()
        lines = text.split("\n")
        if len(lines) == 2 and lines[0].isdigit():
            episode_count = int(lines[0])
            series_name = lines[1]
            user_data[user_id].update({
                "episode_count": episode_count,
                "series_name": series_name,
                "step": "waiting_for_end"
            })
            await message.reply("حالا دستور /end را بزنید تا بتوانید فایل‌ها را ارسال کنید.")
        else:
            await message.reply("فرمت وارد شده صحیح نیست. لطفاً تعداد قسمت‌ها و نام سریال را به فرمت درست وارد کنید.")

# Handle /end command to start receiving files
@app.on_message(filters.command("end") & filters.private)
async def end_command(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id in user_data and user_data[user_id]["step"] == "waiting_for_end":
        user_data[user_id]["step"] = "waiting_for_files"
        await message.reply("حالا فایل‌ها را ارسال کنید. ابتدا تمام کیفیت‌های 360، سپس 480، 540، 720 و 1080.")

# Handle file messages and send them with captions
@app.on_message(filters.document | filters.video & filters.private)
async def handle_files(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id in user_data and user_data[user_id]["step"] == "waiting_for_files":
        data = user_data[user_id]
        series_name = data["series_name"]
        episode_num = len(data.get("files", [])) + 1
        quality = "360"  # اینجا می‌توانید کیفیت فایل‌ها را تعیین کنید یا به طور خودکار شناسایی کنید.

        # Caption template
        caption = (
            f"🎬 {series_name}\n"
            f"🐈 قسمت {episode_num}\n"
            f"زیرنویس چسبیده بدون سانسور🍷\n"
            f"کیفیت: {quality}✨\n"
            f"🫰🏻| @RiRiKdrama | ❤️"
        )

        # Send the file with the caption
        await message.reply_document(
            message.document.file_id, caption=caption
        )

        # Save file data for tracking
        if "files" not in data:
            data["files"] = []
        data["files"].append(message.document.file_id)

# Run the bot
app.run()
