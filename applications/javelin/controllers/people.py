# -*- coding: utf-8 -*-
"""
	Javelin Web2Py People Controller
"""

# metadata
__author__ = "Jeremy Jacobson"
__copyright__ = "(c) 2013, Jacobson and Varni, LLC"
__date__ = "7/5/2013"
__email__ = "jjacobson93@gmail.com"
__data__ = {'name' : 'people', 'label' : 'People', 'description' : 'Keep track of people and edit their data', 
	'icon' : 'user', 'u-icon' : u'\uf007', 'color': 'blue', 'required' : True}

from applications.javelin.ctr_data import ctr_enabled, get_ctr_data
from applications.javelin.private.utils import flattenDict
from gluon.contrib import simplejson as json
from gluon.tools import Service
service = Service(globals())

default_inputs = ['id', 'student_id', 'last_name', 'first_name', 'gender',
	'cell_phone', 'home_phone', 'email', 'street', 'city', 
	'state', 'zip_code', 'notes', 'pic', 'leader']

@auth.requires_login()
@auth.requires_membership('standard')
def index():
	"""Loads the index page for the 'People' controller

	:returns: a dictionary to pass to the view with the list of modules_enabled, the active module ('people') and a dynamic form
	"""
	ctr_data = get_ctr_data()
	return dict(ctr_enabled=ctr_enabled, active_module='people', ctr_data=ctr_data)

@auth.requires_login()
@auth.requires_membership('standard')
@service.json
def data(str_filter=None):
	"""Loads the data for people with an optional filter

	:param str_filter: an optional string filter
	:returns: a list of people
	"""
	if str_filter:
		people = db().select(db.person.ALL, 
			(db.person.last_name.contains(str_filter)) |
			(db.person.first_name.contains(str_filter)) |
			(db.person.id.contains(str_filter))).as_list()
	else:
		people = db().select(db.person.ALL, db.crew.room, 
			left=db.crew.on(db.person.crew==db.crew.id), 
			orderby=db.person.last_name|db.person.first_name).as_list()

	people = [dict((k[-1],v) for k,v in flattenDict(d).items()) for d in people]
	return people

@auth.requires_login()
@auth.requires_membership('standard')
@service.json
def leaders(query=None):
	"""Loads the data for people who are a leader

	:param query: an optional string filter
	:returns: a list of people
	"""
	return [{'id':'all_leaders', 'last_name':'All Leaders', 'first_name' : ''}] + db((db.person.leader==True) 
		& ((db.person.last_name.contains(query)) | (db.person.first_name.contains(query))) ).select(
			db.person.id, db.person.last_name, db.person.first_name, 
			orderby=db.person.last_name|db.person.first_name).as_list()

@auth.requires_login()
@auth.requires_membership('standard')
@service.json
def record(id):
	"""Loads a single record

	:param id: the id of the record to be returned
	:returns: a record dictionary of a person
	"""
	return db.person(id).as_dict()

@auth.requires_login()
@auth.requires_membership('standard')
@service.json
def schedule(id):
	return db(db.person.id==id).select(
			db.course_rec.course_id, db.course.period, 
			db.course.title, db.teacher.teacher_name,
			join=[db.person.on(db.course_rec.student_id==db.person.id),
				db.course.on(db.course_rec.course_id==db.course.id),
				db.teacher.on(db.course.teacher_id==db.teacher.id)],
			orderby=db.course.period)

@auth.requires_login()
@auth.requires_membership('standard')
@service.json
def update_record(id, values):
	"""Updates a record

	:param id: the id of the record
	:returns: a dictionary with a response, either a 0 or 1, depending on success
	"""
	values = json.loads(values)
	response = db(db.person.id==id).update(**dict((k,v) for k,v in values.items() if k in db.person.fields)) # person.update().where(person.c.id==id).values(values).execute()

	return dict(response=response)

@auth.requires_login()
@auth.requires_membership('standard')
@service.json
def update_pic(id, pic):
	"""Updates a picture on a record

	:param id: the id of the record
	:param pic: the picture in base64 encoding
	:returns: a dictionary with a response, either a 0 or 1, depending on success
	"""
	response = db(db.person.id==id).update(pic=pic)

	return dict(response=response)

@auth.requires_login()
@auth.requires_membership('standard')
def call():
	"""Call function used when calling a function from an HTTP request"""
	return service()