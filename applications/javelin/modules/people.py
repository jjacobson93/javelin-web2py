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

# from applications.javelin.models.sqladb import Table, db, metadata
# from applications.javelin.models.db import db
from sqlalchemy.sql.expression import or_
from gluon.http import HTTP

# person = Table('person', metadata, autoload=True)

default_inputs = ['id', 'last_name', 'first_name', 'gender',
	'phone', 'home_phone', 'email', 'street', 'city', 
	'state', 'zip_code', 'notes', 'pic']

def data(str_filter=None):
	if str_filter:
		people = person.select(or_(
			person.c.last_name.contains(str_filter),
			person.c.first_name.contains(str_filter),
			person.c.id.contains(str_filter))).execute().tolist()
	else:
		try:
			people = person.select().order_by('id').execute().tolist()
		except Exception as error:
			print error

	return people

def load_form():
	form = list()
	num_left = len(person.c) - len(default_inputs)
	num = 3
	row = list()

	for c in person.c:
		if c.name not in default_inputs:
			name = str(' ').join([x.capitalize() for x in c.name.split('_')])

			field = { 'span' : num, 'id' : c.name, 'name' : name }

			row.append(field)

			if num_left <= 4:
				num = 12/num_left
			else:
				num_left -= 1

			if len(row) == 4:
				form.append(row)
				row = list()

	return form

def record(id):
	try:
		p = person.select().where(person.c.id==id).execute().fetchone().todict()
	except:
		raise HTTP(500, "Database error. Could not retrieve record")

	return p

def update_record(id, values):
	try:
		person.update().where(person.c.id==id).values(values).execute()
	except:
		raise HTTP(500, "Database error. Could not update record")

	return {'status' : 'success'}

def update_pic(id, pic):
	try:
		person.update().where(person.c.id == id).values(pic=pic).execute()
	except:
		raise HTTP(500, "Database error. Could not update picture")

	return {'status' : 'success'}