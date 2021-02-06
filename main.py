import discord
import os
import asyncio
import urllib.parse

from discord.ext import commands
from riotwatcher import LolWatcher

import sqlite3

discord_token = os.environ["DISCORD_TOKEN"]
lol_token = os.environ["LOL_TOKEN"]

intents = discord.Intents.default()
intents.members = True
intents.presences = True
intents.typing = False

# Create bot
bot = commands.Bot(command_prefix='!', intents=intents)


# Startup Information
@bot.event
async def on_ready():
    print('Connected to bot: {}'.format(bot.user.name))
    print('Bot ID: {}'.format(bot.user.id))


# Commands
@bot.command()
async def train_old(ctx, region, summoner_name):
    discord_name = ctx.author.name
    discord_id = ctx.author.id

    lol_watcher = LolWatcher(lol_token)
    lol_profile = lol_watcher.summoner.by_name(region, summoner_name)
    last_match = lol_watcher.match.matchlist_by_account(
        region, lol_profile.get("accountId")).get("matches")[0]
    match_url = ("https://matchhistory.euw.leagueoflegends.com"
                 f"/en/#match-details/{region}/{last_match.get('gameId')}/")

    message = f"Your discord name: {discord_name},\n\
discord id: {discord_id},\n\
your LoL profile: {lol_profile},\n\
last match: {last_match},\n\
match url: {match_url}"
    await ctx.send(message)


@bot.command()
async def train(ctx):
    message = ctx.message
    author = message.author

    region = await select_region(message)
    profile_url = await make_profile_url(message, region)
    if await confirm_url(author, profile_url):
        save_to_db(author, profile_url)


async def select_region(message: discord.Message):
    author = message.author
    author_name = message.author.name
    await message.author.send(
            f"Hello {author_name}. Please select your region by reacting to "
            "it with 👍:")

    regions = {"EUW1": "Europe West",
               "EUN1": "Europe Nordic & East",
               "RU1": "Russia",
               "NA1": "North America",
               "LA1": "Latin America North",
               "LA2": "Latin America South",
               "BR1": "Brazil",
               "OC1": "Oceania",
               "TR1": "Turkey",
               "JP1": "Japan",
               "KR": "Republic of Korea"}
    sent_messages = []
    for key, value in regions.items():
        sent_messages.append(await author.send(value))

    def check(reaction: discord.Reaction, user: discord.User):
        return (reaction.message in sent_messages and
                reaction.emoji == '👍')

    try:
        reaction, user = await bot.wait_for(
            'reaction_add', timeout=60.0, check=check)
    except asyncio.TimeoutError:
        await author.send("No region chosen, please restart the process")
    else:
        key_list = list(regions.keys())
        val_list = list(regions.values())
        position = val_list.index(reaction.message.content)
        await message.author.send(f'You chose: {reaction.message.content}')
        return key_list[position]


async def make_profile_url(message, region):

    author = message.author
    await message.author.send("Please enter your Leage of Legends username.")

    def check(m: discord.Message):
        return (m.author == author and
                m.channel == message.channel)

    try:
        msg = await bot.wait_for(
            'message', timeout=60.0, check=check)
    except asyncio.TimeoutError:
        await author.send("No username given, please restart the process.")
    else:
        lol_username = msg.content
        await message.author.send(f'Your username: {lol_username}')

    # TODO: add missing urls
    region_url = {"EUW1": "https://euw.op.gg/summoner/userName=",
                  "EUN1": "https://eune.op.gg/summoner/userName=",
                  "RU1": "https://ru.op.gg/summoner/userName=",
                  "NA1": "https://na.op.gg/summoner/userName=",
                  "LA1": "",
                  "LA2": "",
                  "BR1": "",
                  "OC1": "",
                  "TR1": "",
                  "JP1": "",
                  "KR": "",
                  }
    url = region_url[region]

    url_name = urllib.parse.quote(lol_username)
    return f"{url}{url_name}"


async def confirm_url(author, profile_url):
    """Prompts the user to confirm if the url is correct

    :rtype: Bool
    """
    confirmation_message = await author.send(
            "Please check that this is the correct profile: "
            f"{profile_url} \n"
            "If everything is correct, give this message a "
            "👍")

    def check(reaction: discord.Reaction, user: discord.User):
        return (reaction.message == confirmation_message and
                reaction.emoji == '👍')

    try:
        reaction, user = await bot.wait_for(
            'reaction_add', timeout=60.0, check=check)
    except asyncio.TimeoutError:
        await author.send("No reaction given, please restart the process.")
        return False
    else:
        await author.send("Thank you for using our service! We\'ll come "
                          "back to you once we have the analysis.")
        return True
    return False


def save_to_db(author, profile_url):
    conn = sqlite3.connect('lol_train_bro.db')
    """Saves the user information to db"""
    c = conn.cursor()

    # Create table
    c.execute('''SELECT name FROM sqlite_master WHERE type='table' AND
                     name='users';''')

    if c.fetchone()[0] == 0:
        c.execute('''CREATE TABLE users
                  (discord_id text, discord_username text, lol_url text)''')

    # Insert a row of data
    c.execute(f"INSERT INTO users VALUES ('{author.id}',"
              f"'{author.name}','{profile_url}')")

    # Save (commit) the changes
    conn.commit()

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    conn.close()
    print("save to db")


# Run the bot
bot.run(discord_token)
