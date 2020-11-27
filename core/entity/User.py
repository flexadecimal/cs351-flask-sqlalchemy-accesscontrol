from .common import *
# PASSWORD STUFF
import hashlib
import hmac
import os
from secrets import token_bytes
# for encoding back to hex for verifying passwords
from binascii import unhexlify
from datetime import datetime
from .Role import Role

# iterations of hashing algorithm - recommended in python docs
num_hash_iterations = 100000
# salt size, in bytes - for parity, use same size for password hash length
salt_size = 32
# hex digest is twice the size
hash_size = salt_size * 2

@dataclass
class User(Base):
  # dataclass fields for serialization
  email: str
  created: datetime
  password: str
  salt: str
  role_id: int
  Role: Role
  
  __tablename__ = 'User'
  email = Column(String(50), primary_key=True)
  created = Column(DateTime)
  # store salt as well
  password = Column(String(hash_size))
  salt = Column(String(hash_size))
  role_id = Column(Integer, ForeignKey('Role.id'))
  Role = relationship('Role', foreign_keys = [role_id])
  
  def is_admin(self):
    # for checking if a user is an administrator
    admin_singleton = session.query(UserRole).filter_by(name='admin').scalar()
    return Role == admin_singleton
  
  @hybrid_property
  def fullname(self):
    return f"{self.firstname} {self.lastname}"
  
  # PASSWORD STUFF
  @staticmethod
  def __hash(password):
    salt = token_bytes(salt_size)
    password_bytes = password.encode('utf-8')
    #pdb.set_trace()
    hashed = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode(),
        salt,
        num_hash_iterations
    )
    return (hashed.hex(), salt.hex())
  
  @staticmethod
  def __verify(hashed, salt, password):
    hash_bytes = unhexlify(hashed)
    salt_bytes = unhexlify(salt)
    password_bytes = password.encode('utf-8')
    #pdb.set_trace()
    return hmac.compare_digest(
      hash_bytes,
      hashlib.pbkdf2_hmac('sha256', password_bytes, salt_bytes, num_hash_iterations, dklen=salt_size)
    )
    
  # USER FUNCTIONALITY - LOGIN, ETC.
  @classmethod
  def login(cls, email, password):
    user = session.query(User).filter(User.email == email).scalar()
    if user:
      hashed, salt = user.password, user.salt
      # returns User object if successful login, otherwise False
      if cls.__verify(hashed, salt, password):
        return user
    else:
      return False
  
  @classmethod
  def register(cls, email, password):
    hashed, salt = cls.__hash(password)
    now = datetime.now()
    # set role
    user_role = session.query(Role).filter_by(name='User').scalar()
    new = User(
      email = email,
      created = now,
      # save salt
      password = hashed,
      salt = salt,
      Role = user_role
    )
    # add implicitly
    session.add(new)
    session.commit()
    return new