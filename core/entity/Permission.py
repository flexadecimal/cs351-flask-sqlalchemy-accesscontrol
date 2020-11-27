from .common import *
# e.g. object CRUD
@dataclass
class Permission(Base):
  id: int
  module: str
  name: str
  __tablename__ = 'Permission'
  id = Column(Integer, primary_key=True)
  module = Column(String)
  name = Column(String)