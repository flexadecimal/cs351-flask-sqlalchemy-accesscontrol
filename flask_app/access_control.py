import functools
from flask import (
  session as web_session,
  # for custom 403 with permission spec
  abort, redirect, render_template
)
from core import *
# debug
import pdb

# custom 401 that displays permission you don't have
def deny(error, *args):
  #pdb.set_trace()
  permission = error.description['permission']
  return render_template('401.html', permission = permission), 401

def login_required(view):
  """View decorator that redirects anonymous users to the login page."""
  @functools.wraps(view)
  def wrapped_view(**kwargs):
    if 'User' not in web_session:
      return redirect(url_for('auth.login'))
    return view(**kwargs)
  return wrapped_view

def requires_permission(module_name, permission_name):
  error_code = 401
  def decorator(view):
    @functools.wraps(view)
    # also require login
    @login_required
    def wrapped_view(*args, **kwargs):
      # authenticate here - get permission from db
      #pdb.set_trace()
      permission = session.query(entity['Permission']).filter_by(module=module_name, name=permission_name).scalar()
      user = web_session['User']
      # user Role/Permissions are serialized - check that id for permission exists 
      ids = [perm['id'] for perm in user['Role']['Permissions']]
      #pdb.set_trace()
      if permission.id in ids:
        return view(*args, **kwargs)
      else:
        abort(error_code, {
          'permission': permission
        })
    return wrapped_view
  return decorator