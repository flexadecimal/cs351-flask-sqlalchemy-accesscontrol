from .. import *
from ..ViewUtil.ViewUtil import *
from builtins import str


bp = Blueprint(
  'auth',
  __name__,
  template_folder='templates',
  static_folder='static'
)

@bp.route('/login', methods=['POST'])
@bp.route('/', methods=['GET'])
def login():
  if request.method == 'POST':
    username = request.form['email']
    password = request.form['password']
    #pdb.set_trace()
    if request.form['mode'] == 'Login':
      user = entity['User'].login(username, password)
      if user:
        web_session['User'] = user
        g.user = user
        return redirect(url_for('item.show'))
      else:
        flash('Login failed.')
        return render_template('login.html')
    elif request.form['mode'] == 'Register':
      user = entity['User'].register(username, password)
      if user:
        web_session['User'] = user
        g.user = user
        flash('Registration successful.')
      else:
        flash('Registration failed.')
      return redirect('/')
  else:
    return render_template('login.html')
    
@bp.route('/logout')
def logout():
  g.user = None
  web_session.clear()
  return redirect(url_for('auth.login'))

# ROLES STUFF
roles = session.query(entity['Role']).all()
role_id_names = [(role.id, role.name) for role in roles]
#pdb.set_trace()

# password/salt hashes should not be shown
translator = {
  'email': ('Email', lambda user: link_for(bp, user_detail, f'{user.email}', email=user.email)),
  'Role': ('Role', lambda user: str(user.Role.name) if user.Role else 'None')
}

@bp.route('/users/<email>', methods=['GET'])
@requires_permission('User', 'read')
def user_detail(email):
  user = session.query(entity['User']).filter_by(email = email).scalar()
  roles = session.query(entity['Role']).all()
  return render_template('user_detail.html', user=user, roles=roles)

@bp.route('/users/<email>/set_role', methods=['POST'])
@requires_permission('User', 'update')
@requires_permission('Role', 'read')
def set_role(email):
  user = session.query(entity['User']).filter_by(email = email).scalar()
  role = session.query(entity['Role']).filter_by(id = int(request.form['new_role'])).scalar()
  user.Role = role
  session.commit()
  # redirect
  return redirect(url_for('auth.user_detail', email = user.email))

@bp.route('/users')
@requires_permission('User', 'read')
def show():
  #pdb.set_trace()
  singleton = lambda user: redirect(url_for('auth.user_detail', email = user.email))
  return show_table(
    entity['User'],
    translator,
    bp, singleton,
    entity['User'].email
  )