### BEGIN inserted by ~~~SCRIPTNAME~~~ ###

from datetime import datetime
from datetime import timedelta

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import func
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import UnicodeText

from ~~~PROJNAME~~~.models import Base
from ~~~PROJNAME~~~.models import DBSession

class Task(Base):
    __tablename__ = 'task'
    task_id = Column(Integer, primary_key=True)
    name = Column(UnicodeText, nullable=False)
    description = Column(UnicodeText)
 
    @classmethod
    def from_json(cls, data):
        return cls(**data)
 
    def to_json(self):
        to_serialize = ['task_id', 'name', 'description']
        d = {}
        for attr_name in to_serialize:
            d[attr_name] = getattr(self, attr_name)
        return d

### END inserted by ~~~SCRIPTNAME~~~ ###
