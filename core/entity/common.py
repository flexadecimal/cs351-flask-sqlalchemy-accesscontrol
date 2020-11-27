# FOR ENTITY DEFINITIONS
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.orm import column_property
# basic types
from sqlalchemy import (
  Column, Integer, String, DateTime, Numeric, ForeignKey, Table, Float
)

# relationship stuff
from sqlalchemy.orm import (
  relationship, backref, composite, foreign, remote
)
# python dataclasses so we can support automatic JSON serialization (nice to store User object in session)
from dataclasses import dataclass

# FOR CORE
# ...session, meta, engine from core
from .. import session, meta, engine
Base = declarative_base()

from functools import wraps
from dataclasses import dataclass
from typing import List