import json
from pyrogram import Client, filters
from pyrogram.types import Message

with open('config4.json') as config_file:
    config = json.load(config_file)

api_id = int(config['api_id'])
api_hash = config['api_hash']
bot_token = config['bot_token']

app = Client("cap", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

user_data = {}

# Persian ordinal names up to 100
persian_ordinals = [
    "اول", "دوم", "سوم", "چهارم", "پنجم", "ششم", "هفتم", "هشتم", "نهم", "دهم",
    "یازدهم", "دوازدهم", "سیزدهم", "چهاردهم", "پانزدهم", "شانزدهم", "هفدهم", 
    "هجدهم", "نوزدهم", "بیستم", "بیست و یکم", "بیست و دوم", "بیست و سوم", 
    "بیست و چهارم", "بیست و پنجم", "بیست و ششم", "بیست و هفتم", "بیست و هشتم", 
    "بیست و نهم", "سی‌ام", "سی و یکم", "سی و دوم", "سی و سوم", "سی و چهارم",
    # Continue adding more if necessary up to صد (100) or beyond
]

@app.on_message(filters.command("start") & filters.private)
async def start(client: Client, message: Message):
    await message.reply("تعداد قسمت‌ها و نام سریال را به فرمت زیر وارد کنید:\n\n10\n🎬 سریال آقای پلانکتون")
    user_data[message.from_user.id] = {"step": "waiting_for_info", "files": []}

@app.on_message(filters.command("end") & filters.private)
async def end_command(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id in user_data and user_data[user_id]["step"] == "waiting_for_files":
        data = user_data[user_id]
        files = data["files"]
        series_name = data["series_name"]
        episode_count = data["episode_count"]

        if len(files) < episode_count * 5:  # Assuming 5 qualities (360, 480, 540, 720, 1080)
            await message.reply("تعداد فایل‌های ارسال شده کمتر از تعداد لازم است.")
            return

        qualities = ["360", "480", "540", "720", "1080"]
        file_index = 0

        for episode_num in range(1, episode_count + 1):
            # Get the Persian ordinal or fallback to numeric if out of range
            episode_ordinal = persian_ordinals[episode_num - 1] if episode_num <= len(persian_ordinals) else str(episode_num)
            last_part = " (قسمت اخر)" if episode_num == episode_count else ""
            
            for quality in qualities:
                if file_index >= len(files):  # Ensure we don't exceed the number of uploaded files
                    break
                
                file = files[file_index]
                caption = (
                    f"🎬 {series_name}\n"
                    f"🐈 قسمت {episode_ordinal}{last_part}\n"
                    f"زیرنویس چسبیده بدون سانسور🍷\n"
                    f"کیفیت: {quality}✨\n"
                    f"🫰🏻| @RiRiKdrama | ❤️"
                )
                
                # Send each file with its respective caption
                await client.send_document(message.chat.id, file.document.file_id, caption=caption)
                file_index += 1  # Move to the next file

        await message.reply("تمام فایل‌ها با موفقیت ارسال شدند.")
        user_data.pop(user_id, None)

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
                "step": "waiting_for_files"
            })
            await message.reply("فایل‌ها را ارسال کنید. پس از ارسال همه فایل‌ها، دستور /end را بزنید.")
        else:
            await message.reply("فرمت وارد شده صحیح نیست. لطفاً تعداد قسمت‌ها و نام سریال را به فرمت درست وارد کنید.")

@app.on_message((filters.document | filters.video) & filters.private)
async def handle_files(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id in user_data and user_data[user_id]["step"] == "waiting_for_files":
        user_data[user_id]["files"].append(message)
        file_count = len(user_data[user_id]["files"])
        await message.reply(f"فایل شماره {file_count} ذخیره شد.")

# Run the bot
app.run()
