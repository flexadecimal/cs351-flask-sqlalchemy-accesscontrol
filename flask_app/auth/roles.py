from .. import *

from flask_wtf import FlaskForm
import wtforms as wtf
from ..ViewUtil.ViewUtil import *
from builtins import str


bp = Blueprint(
  'roles',
  __name__,
  template_folder='templates',
  static_folder='static'
)

# password/salt hashes should not be shown
translator = {
  'name': ('Role', lambda role: link_for(bp, role_detail, f'{role.name}', id=role.id)),
  'Permissions': ('Permissions', lambda role: ', '.join([f'{perm.module}: {perm.name}' for perm in role.Permissions]))
}

# exclude user, role, permission - only admin should be able to edit these
exclude_modules = ['User', 'Role', 'Permission']

@bp.route('/roles/<id>')
@login_required
@requires_permission('Role', 'read')
def role_detail(id):
  role = session.query(entity['Role']).filter_by(id = id).scalar()
  permissions = session.query(entity['Permission']).filter(entity['Permission'].module.notin_(exclude_modules)).all()
  return render_template('role_detail.html', permissions=permissions, role=role)

@bp.route('/roles/<id>/set_perms', methods = ['POST'])
@login_required
@requires_permission('Role', 'update')
def set_perms(id):
  role = session.query(entity['Role']).filter_by(id = id).scalar()
  perm_ids = request.form.getlist('perms')
  permissions = [session.query(entity['Permission']).filter_by(id=id).scalar() for id in perm_ids]
  # set permissions
  role.Permissions = permissions
  session.commit()
  return redirect(url_for('roles.role_detail', id = id))

@bp.route('/roles/new/', methods=['GET', 'POST'])
@login_required
@requires_permission('Role', 'create')
def new():
  permissions = session.query(entity['Permission']).filter(entity['Permission'].module.notin_(exclude_modules)).all()
  if request.method == 'GET':
    return render_template('add_role.html', permissions = permissions)
  elif request.method == 'POST':
    perm_ids = request.form.getlist('perms')
    permissions = [session.query(entity['Permission']).filter_by(id=id).scalar() for id in perm_ids]
    # make new role and set perms
    new_role = entity['Role'](name = request.form['name'])
    new_role.Permissions = permissions
    # persist
    session.add(new_role)
    session.commit()
    return redirect(url_for('roles.show'))
  else:
    raise NotImplementedError
  
@bp.route('/roles/delete/<id>', methods=['POST'])
@login_required
@requires_permission('Role', 'delete')
def delete(id):
  role = session.query(entity['Role']).filter_by(id=id).scalar()
  session.delete(role)
  session.commit()
  return redirect(url_for('roles.show'))
  
@bp.route('/roles')
@login_required
@requires_permission('Role', 'read')
def show():
  #pdb.set_trace()
  #form = UserRoles()
  #return render_template('users.html', form = form)
  singleton = lambda role: redirect(url_for('roles.role_detail', id = role.id))
  return show_table(
    entity['Role'],
    translator,
    bp, singleton,
    entity['Role'].name,
    actions = {
      url_for('roles.new'): 'New Role'
    }
  )