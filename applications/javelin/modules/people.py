# -*- coding: utf-8 -*-
"""
	Javelin Web2Py People Module
"""

# metadata
__author__ = "Jeremy Jacobson"
__copyright__ = "(c) 2013, Jacobson and Varni, LLC"
__date__ = "7/5/2013"
__email__ = "jjacobson93@gmail.com"
__data__ = {'name' : 'people', 'label' : 'People', 'description' : 'Keep track of people and edit their data', 
	'icon' : 'user', 'u-icon' : u'\uf007', 'required' : True}

from globals import current
from applications.javelin.private.utils import flattenDict

default_inputs = ['id', 'student_id', 'last_name', 'first_name', 'gender',
	'cell_phone', 'home_phone', 'email', 'street', 'city', 
	'state', 'zip_code', 'notes', 'pic', 'leader']

def data(str_filter=None):
	db = current.javelin.db

	if str_filter:
		people = db().select(db.person.ALL, 
			(db.person.last_name.contains(str_filter)) |
			(db.person.first_name.contains(str_filter)) |
			(db.person.id.contains(str_filter))).as_list()
	else:
		people = db().select(db.person.ALL, db.crew.room, left=db.crew.on(db.person.crew==db.crew.id), orderby=db.person.id).as_list()

	people = [dict((k[-1],v) for k,v in flattenDict(d).items()) for d in people]
	return people

def leaders(query):
	db = current.javelin.db

	people = [{'id':'all_leaders', 'last_name':'All Leaders', 'first_name' : ''}] + db((db.person.leader==True) 
		& ((db.person.last_name.contains(query)) | (db.person.first_name.contains(query))) ).select(
			db.person.id, db.person.last_name, db.person.first_name, orderby=db.person.id).as_list()
	return people

def load_form():
	db = current.javelin.db

	form = list()
	num_left = len(db.person.fields) - len(default_inputs)
	num = 3
	row = list()

	for field in db.person.fields:
		if field not in default_inputs:
			name = str(' ').join([x.capitalize() for x in field.split('_')])

			field = { 'span' : num, 'id' : field, 'name' : name }

			row.append(field)

			if num_left <= 4:
				num = 12/num_left
			else:
				num_left -= 1

			if len(row) == 4:
				form.append(row)
				row = list()

	if len(row) > 0:
		form.append(row)

	return form

def record(id):
	db = current.javelin.db
	person = db.person(id).as_dict() # p = person.select().where(person.c.id==id).execute().fetchone().todict()

	return person

def update_record(id, values):
	db = current.javelin.db
	response = db(db.person.id==id).update(**dict((k,v) for k,v in values.items() if k in db.person.fields)) # person.update().where(person.c.id==id).values(values).execute()

	return dict(response=response)

def update_pic(id, pic):
	db = current.javelin.db
	response = db(db.person.id==id).update(pic=pic)

	return dict(response=response)