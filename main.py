from datetime import datetime

import discord
from discord.ext import commands
from sqlalchemy import create_engine, func, delete
from sqlalchemy.orm import sessionmaker
import re

from chances_csgo import roll, get_item
from parser_csgo import CSGO_Item, Item_price, pattern_2, User_info, add_user_info, User_prices

cases = ["The Wildfire Collection",
            "The eSports 2013 Winter Collection",
            "The eSports 2014 Summer Collection",
            "The Breakout Collection",
            "The Phoenix Collection",
            "The Gamma 2 Collection",
            "The Chroma 2 Collection",
            "The Shattered Web Collection",
            "The Chroma 3 Collection",
            "The Prisma Collection",
            "The Safehouse Collection",
            "The Clutch Collection",
            "The Huntsman Collection",
            "The Revolver Case Collection",
            "The Fracture Collection",
            "The Danger Zone Collection",
            "The Operation Hydra Collection",
            "The Falchion Collection",
            "The Operation Broken Fang Collection",
            "The Arms Deal Collection",
            "The Prisma 2 Collection",
            "The Shadow Collection",
            "The CS20 Collection",
            "The Bravo Collection",
            "The Gamma Collection",
            "The Arms Deal 2 Collection",
            "The Vanguard Collection",
            "The Winter Offensive Collection",
            "The Spectrum 2 Collection",
            "The Spectrum Collection",
            "The Chroma Collection",
            "The Arms Deal 3 Collection",
            "The eSports 2013 Collection",
            "The Horizon Collection",
            "The Glove Collection"
]

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
#.filter(CSGO_Item.case == "The Operation Broken Fang Collection")\

def get_price(row):
    correct_name = row.name + " " + "(" + row.quality + ")"
    price_row = session.query(Item_price).filter(Item_price.name == correct_name).first()
    return price_row.price

def count_inventory(unique_user):
    inventory_price = 0
    new_rows = session.query(User_info).filter(User_info.user == str(unique_user)).all()
    if new_rows:
        for new_row in new_rows:
            other_row = session.query(Item_price).filter(Item_price.name == new_row.item).first()
            inventory_price += other_row.price
    added_row = User_prices(user=str(unique_user), price=inventory_price)
    session.add(added_row)
    session.commit()
    return inventory_price


# Commands
@bot.command()
async def open_case(ctx, user_case=""):
    message = ctx.message
    author = message.author
    weapon_rarity, weapon_quality, weapon_stattrack = get_item()
    # print(weapon_rarity, weapon_quality, weapon_stattrack)
    for _ in range(1):
        if user_case == "":
            row = session.query(CSGO_Item)\
                .filter(CSGO_Item.rarity == weapon_rarity)\
                .filter(CSGO_Item.quality == weapon_quality)\
                .filter(CSGO_Item.stattrak == weapon_stattrack).order_by(func.random()).first()
        elif user_case in cases:
            row = session.query(CSGO_Item).filter(CSGO_Item.case == user_case)\
                .filter(CSGO_Item.rarity == weapon_rarity) \
                .filter(CSGO_Item.quality == weapon_quality) \
                .filter(CSGO_Item.stattrak == weapon_stattrack).order_by(func.random()).first()
        else:
            await ctx.send("Упс! Кажется вы ввели несуществующий кейс!")
            break;

        weapon_name = row.name + " " + "(" + row.quality + ")"
        time_opened = datetime.now()
        add_user_info(str(author), str(weapon_name), str(time_opened))

        url = "https://community.cloudflare.steamstatic.com/economy/image/" + row.image_url + "/360fx360f"

        if weapon_stattrack:
            weapon_stattrack = "★ StatTrak™"
        else:
            weapon_stattrack = ""

        my_embed = discord.Embed(title="{weapon_stattrak} {item}"
                                 .format(item=row.name, weapon_stattrak=weapon_stattrack)
                                 , color=rarity_color[weapon_rarity])
        my_embed.add_field(name="КАЧЕСТВО & ФЛОТ:", value="{rarity} \n {flot}".format(rarity=rarity_translate[row.rarity]
                                            , flot=quality_translate[row.quality]), inline=True)
        my_embed.add_field(name="ЦЕНА", value="{price} руб".format(price=get_price(row)))
        my_embed.set_author(name="{author}, ты выбил из {case}:"
                                 .format(author=author, case=row.case), icon_url="https://csgocases.com/uploads/gallery/oryginal/dedc1450e94dabc3e7593a3b51e20833bba834d6.png")
        my_embed.set_image(url=url)
        await ctx.send(embed=my_embed)

@bot.command()
async def inventory_prices(ctx):
    message = ctx.message
    author = message.author
    user_rows = session.query(User_info).all()
    users = []
    for user_row in user_rows:
        users.append(user_row.user)
    individual_users = set(users)
    users_list = list(individual_users)
    for unique_user in users_list:
        stmt = delete(User_prices).where(User_prices.user == unique_user).execution_options(synchronize_session="fetch")
        session.execute(stmt)
        session.commit()
        count_inventory(unique_user)
    if len(users_list) >= 5:
        leader_rows = session.query(User_prices).order_by(User_prices.price).all()
        n = 0
        string_for_message = " "
        for index, value in enumerate(leader_rows):
            while n != 5:
                string_for_message += "{index}: {user} ({price} руб)\n".format(index=(index + 1), user=value.user, price=value.price)
                n += 1
    else:
        leader_rows = session.query(User_prices).order_by(User_prices.price).all()
        n = 0
        string_for_message = " "
        for index, value in enumerate(leader_rows):
            while n != len(users_list):
                string_for_message += "{index}: {user} ({price} руб)\n".format(index=(index + 1), user=value.user, price=value.price)
                n += 1
    url = "https://i.redd.it/xknufjrmzy341.png"
    icon_url = "https://cdn2.iconfinder.com/data/icons/popular-games-1/50/csgo_squircle-512.png"
    author_price = count_inventory(author)
    embed_message = discord.Embed(title=string_for_message, color=0xFFD700)
    embed_message.set_author(name="ТОП ПОЛЬЗОВАТЕЛЕЙ ПО СТОИМОСТИ ИНВЕНТАРЯ:", icon_url=icon_url)
    embed_message.add_field(name="{author}, ВАШ ИНВЕНТАРЬ СТОИТ:".format(author=author), value="{price} руб".format(price=author_price), inline=True)
    embed_message.set_image(url=url)
    await ctx.send(embed=embed_message)





# Run the bot
bot.run(discord_token)
