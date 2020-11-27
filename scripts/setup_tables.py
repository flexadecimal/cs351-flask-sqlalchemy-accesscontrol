#!/usr/bin/env python
# little hack because we run from the scripts folder
import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from core import *

from itertools import product
import pdb

associations = [
  'role_permission_association',
]

# see https://stackoverflow.com/questions/2546207/does-sqlalchemy-have-an-equivalent-of-djangos-get-or-create
def get_or_create(session, model, **kwargs):
  instance = session.query(model).filter_by(**kwargs).first()
  if instance:
    return instance
  else:
    instance = model(**kwargs)
    session.add(instance)
    session.commit()
    return instance

if __name__ == '__main__':
  with engine.connect() as connection:
    # entities + junction tables
    tables = dict(
      meta.tables,
      **{name: entity.__table__ for name, entity in entity.items()},
    )
    # drop/add tables
    for name, table in tables.items():
      # drop if exists
      if connection.dialect.has_table(engine, name):
        table.drop(engine)
        session.commit()
      # create
      table.create(engine)
      session.commit()
    # make entity CRUD permissions if they don't exist
    # basically all permissions are just cross join of Entity X CRUD - because this is just for objects like an ACL
    crud = ['create', 'read', 'update', 'delete']
    permissions = [entity['Permission'](module=entity_name, name=operation) for entity_name, operation in product(entity.keys(), crud)]
    session.add_all(permissions)
    # DEMO ROLES
    # create admin role with all permissions...
    admin_role = get_or_create(session, entity['Role'], name='Admin')
    admin_role.Permissions = permissions
    # create user role with non-user/role/permission permissions
    exclude_modules = ['User', 'Role', 'Permission']
    user_permissions = [perm for perm in permissions if perm.module not in exclude_modules and perm.name != 'delete']
    user_role = get_or_create(session, entity['Role'], name='User')
    user_role.Permissions = user_permissions
    # create readonly visitor role - can list and detail, but no update/delete
    read_permissions = [perm for perm in permissions if perm.module not in exclude_modules and perm.name == 'read']
    visitor_role = get_or_create(session, entity['Role'], name='Visitor')
    item_read = session.query(entity['Permission']).filter_by(module='Item', name='read').scalar()
    visitor_role.Permissions = read_permissions
    # DEMO ACCOUNTS
    accounts = {
      'admin@world.com': ('helloworld', admin_role),
      'user@world.com': ('helloworld', user_role),
      'visitor@world.com': ('helloworld', visitor_role)
    }
    for email, pass_role in accounts.items():
      password, role = pass_role
      if not session.query(entity['User']).filter_by(email=email).scalar():
        user = entity['User'].register(email, password)
        user.Role = role
      session.add(user)
    session.commit()
    # dummy items from lorem ipsum
    lorem = '''
    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam pellentesque mauris leo, vitae placerat felis lacinia sit amet. Maecenas ultrices dapibus purus, eu feugiat leo molestie a. Curabitur sed nibh id arcu tincidunt tempor quis eget felis. Nunc varius, turpis ac dignissim placerat, felis diam dapibus nisl, at eleifend neque. 
    '''
    items = [entity['Item'](name = word) for word in lorem.split()]
    session.add_all(items)
    session.commit()
    pass