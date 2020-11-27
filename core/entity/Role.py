from .common import *
from .Permission import Permission

@dataclass
class Role(Base):
  id: int
  name: str
  Permissions: List[Permission]
  __tablename__ = 'Role'
  # e.g. Admin, Worker, etc.
  id = Column(Integer, primary_key=True)
  name = Column(String)
  Permissions = relationship(
    'Permission',
    # string table, late bound
    secondary=lambda: meta.tables['role_permission_association']
  )
  
# need association table for many to many - Role has many permissions, Permissions can be in many Roles
role_permission_association = Table(
  'role_permission_association',
  meta,
  Column('Role_id', Integer, ForeignKey(Role.id)),
  Column('Permission_id', Integer, ForeignKey(Permission.id)),
)