import asyncio
import sys

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import discord
import requests
import os
import uuid
import json
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
API_KEY = os.getenv('LINK4M_API_KEY')
FLASK_URL = 'http://127.0.0.1:5000'
GUILD_ID = os.getenv('GUILD_ID')  # Thêm ID của server (guild) vào file .env

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

data_file = 'user_data.json'

def load_data():
    if os.path.exists(data_file):
        with open(data_file, 'r') as file:
            return json.load(file)
    return {}

def save_data(data):
    with open(data_file, 'w') as file:
        json.dump(data, file, indent=4)

user_data = load_data()

def shorten_link(hwid):
    full_url = f'{FLASK_URL}/generate?hwid={hwid}'
    api_endpoint = f'https://link4m.co/st?api={API_KEY}&url={full_url}'
    response = requests.get(api_endpoint)
    if response.status_code == 200:
        return response.text
    else:
        return None

def increment_progress(user_id):
    if user_id not in user_data:
        user_data[user_id] = {'points': 0, 'robux': 0, 'links': 0}
    user_data[user_id]['links'] += 1
    save_data(user_data)
    return user_data[user_id]['links']

def has_completed_task(user_id, required_links=3):
    return user_data.get(user_id, {}).get('links', 0) >= required_links

def reset_progress(user_id):
    if user_id in user_data:
        user_data[user_id]['links'] = 0
    save_data(user_data)

def add_point(user_id):
    if user_id not in user_data:
        user_data[user_id] = {'points': 0, 'robux': 0, 'links': 0}
    user_data[user_id]['points'] += 1
    save_data(user_data)

def add_robux(user_id, amount):
    if user_id not in user_data:
        user_data[user_id] = {'points': 0, 'robux': 0, 'links': 0}
    user_data[user_id]['robux'] += amount
    save_data(user_data)

@bot.event
async def on_ready():
    await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
    print(f'Logged in as {bot.user}')

@bot.tree.command(name="shorten", description="Generate a shortened link")
async def shorten(interaction: discord.Interaction):
    hwid = str(uuid.uuid4())
    shortened_url = shorten_link(hwid)

    if shortened_url:
        await interaction.user.send(f'Link rút gọn: {shortened_url}')
        await interaction.response.send_message('Link rút gọn đã được gửi riêng cho bạn!', ephemeral=True)
    else:
        await interaction.response.send_message('Có lỗi xảy ra khi tạo link rút gọn.')

@bot.tree.command(name="key", description="Kiểm tra key và nhận điểm")
async def key_command(interaction: discord.Interaction, key: str):
    if key in valid_keys:
        add_point(str(interaction.user.id))
        valid_keys.remove(key)  # Remove key so it can't be reused
        await interaction.response.send_message('Key đúng! Bạn nhận được 1 điểm.')
    else:
        await interaction.response.send_message('Key sai! Vui lòng thử lại.')

@bot.tree.command(name="doipoint", description="Đổi điểm lấy Robux")
async def doipoint(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    if user_data.get(user_id, {}).get('points', 0) >= 3:
        user_data[user_id]['points'] -= 3
        add_robux(user_id, 1)
        await interaction.response.send_message('Bạn đã đổi 3 điểm thành 1 Robux.')
        save_data(user_data)
    else:
        await interaction.response.send_message('Bạn không đủ điểm để đổi Robux.')

bot.run(TOKEN)
