import discord
from discord.ext import commands
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from chances_csgo import roll, get_item
from parser_csgo import CSGO_Item

discord_token = 'Nzk5OTU3MTQzMDYyODM5MzU4.YALIJQ.LkzI7FZGpB1thH6CGigwAnb_79I'

intents = discord.Intents.default()
intents.members = True
intents.presences = True
intents.typing = False

# Create bot
bot = commands.Bot(command_prefix='!', intents=intents)


# Connect to DB
engine = create_engine('sqlite:///csgo.db?check_same_thread=False')
Session = sessionmaker(bind=engine)
session = Session()
weapon_rarity, weapon_quality, weapon_stattrack = get_item()
print(weapon_rarity, weapon_quality, weapon_stattrack)
for row in session.query(CSGO_Item).filter(CSGO_Item.rarity == weapon_rarity).all():
    print(row)

# Startup Information
@bot.event
async def on_ready():
    print('Connected to bot: {}'.format(bot.user.name))
    print('Bot ID: {}'.format(bot.user.id))


# Commands
@bot.command()
async def train(ctx):
    message = ctx.message
    author = message.author


    await ctx.send(message)

# Run the bot
# bot.run(discord_token)
