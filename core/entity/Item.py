from .common import *

# dummy item - just so we have something to list that isnt auth related.
class Item(Base):
  __tablename__ = 'Item'
  id = Column(Integer, primary_key=True)
  name = Column(String)