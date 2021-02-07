import discord
from discord.ext import commands
from sqlalchemy import create_engine, func
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


# Startup Information
@bot.event
async def on_ready():
    print('Connected to bot: {}'.format(bot.user.name))
    print('Bot ID: {}'.format(bot.user.id))

rarity_translate = {"Mil-Spec Grade":"Армейское (синее)",
          "Restricted":"Запрещённое (фиолетовое)",
          "Classified":"Засекреченное (розовое)",
          "Covert":"Тайное (красное)"}

quality_translate = {"Battle-Scarred":"Закалённый в боях",
           "Well-Worn":"Поношенный",
           "Field-Tested":"После полевых испытаний",
           "Minimal Wear":"Немного поношенный",
           "Factory New":"Прямо с завода"}

rarity_color = {"Mil-Spec Grade":0x0000FF,
          "Restricted":0x800080,
          "Classified":0xFF00FF,
          "Covert":0xFF0000}

# Commands
@bot.command()
async def open_case(ctx):
    message = ctx.message
    author = message.author
    weapon_rarity, weapon_quality, weapon_stattrack = get_item()
    print(weapon_rarity, weapon_quality, weapon_stattrack)
    row = session.query(CSGO_Item).filter(CSGO_Item.case == "The Huntsman Collection")\
        .filter(CSGO_Item.rarity == weapon_rarity)\
        .filter(CSGO_Item.quality == weapon_quality)\
        .filter(CSGO_Item.stattrak == weapon_stattrack).order_by(func.random()).first()

    # print(row)
    if weapon_stattrack:
        weapon_stattrack = "★ StatTrak™"
    else:
        weapon_stattrack = ""
    # result = '''{author}, ты выбил из {case}: {weapon_stattrak} {item}.
    # Качества: {rarity} | {flot}.
    # Осмотреть в игре: {url}'''.format(author=author
    #                                     , case=row.case
    #                                     , item=row.name
    #                                     , rarity=rarity_translate[row.rarity]
    #                                     , flot=quality_translate[row.quality]
    #                                     , url=row.inspect_url
    #                                     , weapon_stattrak=weapon_stattrack)
    my_embed = discord.Embed(title="{author}, ты выбил из {case}:"
                             .format(author=author, case=row.case),
                             description="{weapon_stattrak} {item}"
                             .format(item=row.name, weapon_stattrak=weapon_stattrack)
                             , color=rarity_color[weapon_rarity])
    my_embed.add_field(name="Качество & Флот:", value="{rarity} \n {flot}".format(rarity=rarity_translate[row.rarity]
                                        , flot=quality_translate[row.quality]))
    my_embed.add_field(name="Осмотреть в игре:", value="{url}".format(url=row.inspect_url))
    my_embed.set_author(name="CASE OPENER")
    await ctx.send(embed=my_embed)

# Run the bot
bot.run(discord_token)
