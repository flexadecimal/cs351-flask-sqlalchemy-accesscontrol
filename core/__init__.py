import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
# datetime stuff
from datetime import datetime
# for parsing environment variables
from os import environ as env

# see scripts in top level folder
#max_server = env['RDS_HOSTNAME']
#max_user = env['RDS_USERNAME']
#max_password = env['RDS_PASSWORD']
#max_db = env['RDS_DB_NAME']

server = 'sqlite:///test.db'
engine = sqlalchemy.create_engine(server, echo=True)

# SET UP AND PROVIDE [session, meta, engine] FOR CORE
session_factory = sessionmaker()
session_factory.configure(bind=engine)

session = session_factory()
meta = sqlalchemy.schema.MetaData(bind=engine)

# IMPORT ENTITIES
from .entity import *
 
# ... a little hack - to avoid ugly namespaces like `User.User`, make an entity dict,
# e.g. entity['User'] = class User
entity = {klass: getattr(getattr(entity, klass), klass) for klass in entity.__all__}
__all__ = ['session', 'meta', 'engine', 'entity']