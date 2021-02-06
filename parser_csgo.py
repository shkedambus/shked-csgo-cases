import json
import re
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, Boolean
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///csgo.db?check_same_thread=False')
Base = declarative_base()

class Table(Base):
    __tablename__ = 'task'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    rarity = Column(String)
    quality = Column(String)
    stattrak = Column(Boolean)
    case = Column(String, default="No collection")
    image_url = Column(String)
    inspect_url = Column(String)



    def __repr__(self):
        return self.string_field

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

pattern = r"(★?[a-zA-Z0-9- ]* \| [a-zA-Z0-9- ]*) (\([a-zA-Z- ]*\))"

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
        stattrack = "StatTrak" in key
        search = re.search(pattern, key)
        if search:
            item_name = search.group(1)
        new_row = Table(name=item_name,
                        rarity=item_rarity,
                        quality=item_quality,
                        stattrak=stattrack,
                        case=item_case,
                        image_url=item_image,
                        inspect_url=inspect_url)
        session.add(new_row)
    session.commit()