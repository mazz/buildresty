### BEGIN inserted by ~~~SCRIPTNAME~~~ ###

from datetime import datetime
from datetime import timedelta

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import func
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import UnicodeText
from sqlalchemy import ForeignKey

from ~~~PROJNAME~~~.models import Base
from ~~~PROJNAME~~~.models import DBSession

class Task(Base):
    __tablename__ = 'tasks'
    tid = Column(Integer, primary_key=True)
    name = Column(UnicodeText, nullable=False)
    description = Column(UnicodeText)
    username = Column(Unicode(255), ForeignKey('users.username'), nullable=False,)
    
    @classmethod
    def from_json(cls, data):
        return cls(**data)
 
    def to_json(self):
        to_serialize = ['tid', 'name', 'description']
        d = {}
        for attr_name in to_serialize:
            d[attr_name] = getattr(self, attr_name)
        return d

### END inserted by ~~~SCRIPTNAME~~~ ###
