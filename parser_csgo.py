import json
import re
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, Boolean
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///csgo.db?check_same_thread=False')
Base = declarative_base()

class User_info(Base):
    __tablename__ = 'user_info'
    id = Column(Integer, primary_key=True)
    user = Column(String)
    item = Column(String)
    opened_at = Column(Date)

    def __repr__(self):
        return '''<Item(user={user},
                     item={item},
                     opened_at={opened_at}>'''\
            .format(user=self.user,
                    item=self.item,
                    opened_at=self.opened_at)

class Item_price(Base):
    __tablename__ = 'csgo_prices'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Integer)

    def __repr__(self):
        return '''<Item(name={name},
                     price={price}>'''\
            .format(name=self.name,
                    price=self.price)

class CSGO_Item(Base):
    __tablename__ = 'csgo_items'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    rarity = Column(String)
    quality = Column(String)
    stattrak = Column(Boolean)
    case = Column(String, default="No collection")
    image_url = Column(String)
    inspect_url = Column(String)



    def __repr__(self):
        return '''<Item(name={name},
                     rarity={rarity},
                     quality={quality},
                     stattrak={stattrak},
                     case={case}>'''\
            .format(name=self.name,
                    rarity=self.rarity,
                    quality=self.quality,
                    stattrak = self.stattrak,
                    case=self.case)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

with open("response_prices.json", "r", encoding="utf8") as json_file:
    prices_dict = json.load(json_file)
    prices = prices_dict["result"]["prices"]
    for key, value in prices.items():
        for val in value.keys():
            if val == "7":
                name_of_item = key
                item_price = int(value[val]["avg"] * 74.04)
                row = Item_price(name=name_of_item, price=item_price)
                session.add(row)
    session.commit()

pattern = r"(★?[a-zA-Z0-9- ]* \| [a-zA-Z0-9- ]*) (\([a-zA-Z- ]*\))"
pattern_2 = r"(★?[a-zA-Z0-9- ]* \| [a-zA-Z0-9- ]*)"

with open("response.json", "r", encoding="utf8") as json_file:
    response_dict = json.load(json_file)
    items = response_dict["result"]["items"]
    for key, item in items.items():
        tags = item["tags"]
        for tag in tags:
            if tag["category_name"] == "Collection":
                item_case = tag["name"]
            elif tag["category_name"] == "Quality":
                item_rarity = tag["name"]
            elif tag["category_name"] == "Exterior":
                item_quality = tag["name"]
        item_image = item["icon_url"]
        actions = item["actions"]
        for action in actions:
            for key_name in action.keys():
                if action[key_name] == "Inspect in Game...":
                    inspect_url = action["link"]
        stattrak = "StatTrak" in key
        search = re.search(pattern, key)
        if search:
            item_name = search.group(1).strip()
        new_row = CSGO_Item(name=item_name,
                        rarity=item_rarity,
                        quality=item_quality,
                        stattrak=stattrak,
                        case=item_case,
                        image_url=item_image,
                        inspect_url=inspect_url)
        session.add(new_row)
    session.commit()