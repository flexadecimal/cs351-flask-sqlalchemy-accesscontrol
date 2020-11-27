from .. import *
from flask.views import View
from math import ceil
import pdb
      
 # make a link using url_for
def link_for(bp, func, text, **kwargs):
  bp_method = f"{bp.name}.{func.__name__}"
  href = url_for(bp_method, **kwargs)
  a_tag = f"<a href='{href}'>{text}</a>"
  return a_tag
  
# takes query object, e.g. passing search query so its results can be paginated
def paginated_table(query, translator, orderby_translator, page_size, page_index, orderby, name, bp, form, actions):
  #pdb.set_trace()
  num_total = query.count()
  num_pages = ceil(num_total / page_size)
  # page logic - paginate if we have more results than fit in one
  if num_total > page_size:
    # 1-indexed, because this is made for humans
    page = query.order_by(orderby).limit(page_size).offset(page_size * (page_index - 1)).all()
  # otherwise... just return the single page
  else:
    page = query.order_by(orderby).all()
  return render_template(
    'table.html',
    collection=page,
    translator=translator,
    orderby_translator=orderby_translator,
    num_pages=num_pages,
    current_page=page_index,
    entity_name=name,
    bp=bp,
    form=form,
    actions=actions
  )

def is_relationship_attr(attr):
  return attr.comparator.__module__ == 'sqlalchemy.orm.relationships'

def show_table(base_entity, translator, bp, singleton_func, orderby=None, page=1, page_size=15, form=False, actions={}):
  display_query = session.query(base_entity)
  # add search to query, if specified
  if 'search' in request.args and request.args['search'] != '':
    #pdb.set_trace()
    search_field = request.args['search_field']
    search_text = request.args['search']
    search_attribute = getattr(base_entity, search_field)
    # if relationship, we need to join to the relationship filter clause
    if is_relationship_attr(search_attribute):
      klass = entity[search_attribute.key]
      display_query = display_query.join(klass).filter(getattr(klass, search_attribute.__name__).like(f"{search_text}%"))
    # regular attribute
    else:
      display_query = display_query.filter(search_attribute.like(f"{search_text}%"))
  # for orderby dialog - don't include relationship properties in the ordering options, because it isn't implemented
  # TODO: implement ordering for relationship attributes in some sort of ViewModel class
  orderby_translator = {field: name_func_tuple for field, name_func_tuple in translator.items() if not is_relationship_attr(getattr(base_entity, field))}
  if 'orderby_field' in request.args:
    orderby = getattr(base_entity, request.args['orderby_field'])
    # asc/desc
    if request.args['sort'] == 'desc':
      orderby = orderby.desc()
    elif request.args['sort'] == 'asc':
      orderby = orderby.asc()
    else:
      raise NotImplementedError
  # default orderby - first field
  else:
    first_field = list(translator.keys())[0]
    orderby = getattr(base_entity, first_field).asc()
  # pagination
  if 'page' in request.args:
    page = int(request.args['page'])
  
  # polymorphic display: if one result is found, show its detail, otherwise show a table
  table_name = base_entity.__name__
  result_count = display_query.count()
  if result_count > 1:
    return paginated_table(display_query, translator, orderby_translator, page_size, page, orderby, table_name, bp, form, actions)
  elif result_count == 1:
    #pdb.set_trace()
    item = display_query.scalar()
    return singleton_func(item)
  # no objects - show all, but warn that search was invalid
  elif result_count == 0:
    flash('No results found - showing all.')
    return paginated_table(session.query(base_entity), translator, orderby_translator, page_size, page, orderby, table_name, bp, form, actions)