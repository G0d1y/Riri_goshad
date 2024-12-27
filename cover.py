import json
import os
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from PIL import Image, ImageFilter
from pyrogram.types import ReplyKeyboardMarkup
import shutil

with open('c-config.json') as config_file:
    config = json.load(config_file)

api_id = int(config['api_id'])
api_hash = config['api_hash']
bot_token = config['bot_token']

app = Client("cover", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

user_states = {}
DOWNLOAD_FOLDER = "./downloads"

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    await message.reply_text(
        ";)"
    )
    
def clear_downloads_folder():
    if not os.path.exists(DOWNLOAD_FOLDER):
        print(f"The folder {DOWNLOAD_FOLDER} does not exist.")
        return

    for item in os.listdir(DOWNLOAD_FOLDER):
        item_path = os.path.join(DOWNLOAD_FOLDER, item)
        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
            print(f"Deleted: {item_path}")
        except Exception as e:
            print(f"Failed to delete {item_path}: {e}")

@app.on_message(filters.document)
async def handle_media(client: Client, message: Message):
    user_id = message.from_user.id

    user_states[user_id] = {"stage": "awaiting_name", "type": "document" , "file_id": message.document.file_id,"cover_path": "" , "name": "" , "cap": ""}
    clear_downloads_folder()
    await message.reply_text(
        "لطفاً نام جدید فایل را ارسال کنید:"
    )
@app.on_message(filters.video)
async def handle_media(client: Client, message: Message):
    user_id = message.from_user.id

    user_states[user_id] = {"stage": "awaiting_name", "type": "video" , "file_id": message.video.file_id,"cover_path": "" , "name": "" , "cap": ""}
    clear_downloads_folder()
    await message.reply_text(
        "لطفاً نام جدید فایل را ارسال کنید:"
    )
      
@app.on_message(filters.text & filters.private)
async def handle_button(client, message):
    user_id = message.from_user.id
    state = user_states.get(user_id, {}).get("stage")
    type = user_states[user_id]["type"]
    ext = ".mkv"
    if type == "video":
        ext = ".mp4"
    if state == "awaiting_name":
        name = message.text


        file_path = os.path.join(DOWNLOAD_FOLDER, f"{name}{ext}")
        file_id = user_states[user_id]["file_id"]
        await message.reply_text("درحال دانلود...")
        await client.download_media(file_id, file_path)
        user_states[user_id]["name"] = message.text
        user_states[user_id]["stage"] = "awaiting_cover"
        await message.reply_text("لطفاً کاور جدید فایل را ارسال کنید:")
    elif state == "awaiting_caption":
        user_states[user_id]["cap"] = message.text
        file_id = user_states[user_id]["file_id"]
        cover = user_states[user_id]["cover_path"]
        cap = user_states[user_id]["cap"]
        name = user_states[user_id]["name"]
        path = DOWNLOAD_FOLDER + "/" + name + ext
        if type == "document":
            await client.send_document(user_id, path, thumb= cover, caption= cap)
        elif type == "video":
            await client.send_video(user_id, path, thumb= cover, caption= cap)


@app.on_message(filters.photo & filters.private)
async def handle_cover(client, message):
    user_id = message.from_user.id
    cover_image_path = f"{user_id}_thumb.jpg"
    if os.path.exists(cover_image_path):
        os.remove(cover_image_path)
    thumbnail_path = os.path.join(DOWNLOAD_FOLDER, cover_image_path)
    await message.download(thumbnail_path)    
    user_states[user_id]["cover_path"] = thumbnail_path
    user_states[user_id]["stage"] = "awaiting_caption"
    await message.reply("عکس کاور دریافت شد...")
    await message.reply_text("لطفاً کپشن جدید فایل را ارسال کنید:")




app.run()
