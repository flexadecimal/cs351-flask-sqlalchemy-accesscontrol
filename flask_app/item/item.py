from .. import *
from ..ViewUtil.ViewUtil import *

from builtins import str

bp = Blueprint(
  'item',
  __name__,
  template_folder='templates',
  static_folder='static'
)

translator = {
  'id': ('ID', lambda item: str(item.id)),
  'name': ('Name', lambda item: link_for(bp, part_detail, item.name, id=item.id)),
}

# detail page
@bp.route('/item/part/<id>', methods=['GET'])
@requires_permission('Item', 'read')
def part_detail(id):
  item = session.query(entity['Item']).filter_by(id = id).scalar()
  return render_template('part_detail.html', item=item)

@bp.route('/item/<id>/set_name', methods=['POST'])
@requires_permission('Item', 'update')
def set_name(id):
  item = session.query(entity['Item']).filter_by(id = id).scalar()
  # set name 
  item.name = request.form['name']
  session.commit()
  return render_template('part_detail.html', item=item)

@bp.route('/item/<id>/delete', methods=['POST'])
@requires_permission('Item', 'delete')
def delete(id):
  item = session.query(entity['Item']).filter_by(id = id).scalar()
  # delete
  session.delete(item)
  session.commit()
  # redirect  
  return redirect(url_for('item.show'))

@bp.route('/items/', methods=['GET'])
@requires_permission('Item', 'read')
def show():
  singleton = lambda item: redirect(url_for('item.part_detail', id = item.id))
  return show_table(
    entity['Item'],
    translator,
    bp, singleton,
  )