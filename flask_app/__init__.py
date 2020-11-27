import os
from flask import (
  Flask, Blueprint, g, redirect, render_template, request, url_for, flash,
)
from secrets import token_urlsafe
# for debug
import pdb

# access control decorators
from .access_control import *

# namespace hack :(
import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from core import *

# register blueprints and such
def create_app():
  app = Flask(__name__)
  with app.app_context():
    # register blueprints with main app
    from .auth import auth
    from .auth import roles
    # basic entity, so we have something to list
    from .item import item
    # SECURITY
    # need this for serialized user object in session
    app.config['SECRET_KEY'] = token_urlsafe(32)
    # register deny handler
    app.register_error_handler(401, deny)
    
    # register blueprints
    app.register_blueprint(auth.bp)
    app.register_blueprint(roles.bp)
    app.register_blueprint(item.bp)
    return app

# for debug
if __name__ == "__main__":
  app = create_app()
  app.run(debug=True)
  pass