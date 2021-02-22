from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, Boolean
from sqlalchemy.orm import sessionmaker
import parser_csgo

class User_info(parser_csgo.Base):
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