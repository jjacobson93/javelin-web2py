# -*- coding: utf-8 -*-
"""
	Javelin Web2Py Groups Module
"""

# metadata
__author__ = "Jeremy Jacobson"
__copyright__ = "(c) 2013, Jacobson and Varni, LLC"
__date__ = "7/9/2013"
__email__ = "jjacobson93@gmail.com"
__data__ = {'name' : 'groups', 'label' : 'Groups', 'description' : 'Create groups and add people to them', 
	'icon' : 'book', 'u-icon' : u'\uf02d', 'required' : True}

from globals import current
from gluon.http import HTTP

def data():
	db = current.javelin.db
	groups = db().select(db.groups.ALL, orderby=db.groups.name).as_list()
	
	return groups

	# raise HTTP(500, "Database error. Could not get records")

def records(id):
	db = current.javelin.db
	result = db(db.group_rec.group_id==id).select(
		db.person.id, db.person.last_name, db.person.first_name,
		join=db.group_rec.person_id==db.person.id).as_list()
	
	if result:
		return result

	raise HTTP(500, "Database error. Could not get records")

def add_group(name, description, values):
	try:
		# Insert new group
		group.insert().values({'name' : name, 'description' : description}).execute()
		# Select group
		g = group.select().where(group.c.name==name).execute().fetchone()

		group_rec.insert().values([{'group_id' : g.id, 'person_id' : x} for x in values]).execute()
	except:
		raise HTTP(500, "Database error. Could not add group")

	return {'status' : 'success'}

def add_to_group(person_id, group_id):
	try:
		group_rec.insert().values({'person_id' : person_id, 'group_id' : group_id})
	except:
		raise HTTP(500, "Database error. Could not add to group")

	return {'status' : 'success'}

def delete_group(id):
	try:
		group.delete().where(group.c.id==id).execute()
	except:
		raise HTTP(500, "Database error. Could not delete group")

	return {'status' : 'success'}

def delete_from_group(person_id, group_id):		
	try:
		group_rec.delete().where(and_(group_rec.c.person_id==person_id, 
			group_rec.c.group_id==group_id)).execute()
	except:
		raise HTTP(500, "Database error. Could not add group")
	
	return {'status' : 'success'}

def edit_group(id, name, description):
	try:
		group.update().where(group.c.id==id).values({'name' : name, 'description' : description}).execute()
	except:
		raise HTTP(500, "Database error. Could not add group")

	return {'status' : 'success'}

def get_people():
	try:
		people = person.select().execute().fetchall()
	except:
		raise HTTP(500, "Database error. Could not get people")

	result = []
	for p in people:
		result.append({'value' : str(p.id), 'label' : p.last_name + ", " + p.first_name})
	
	return result