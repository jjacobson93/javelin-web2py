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
from applications.javelin.private.utils import flattenDict

def data():
	db = current.javelin.db
	count = db.person.id.count()
	groups = db().select(
		db.groups.ALL, count.with_alias('count'),
		left=[db.group_rec.on(db.groups.id==db.group_rec.group_id), 
			db.person.on(db.person.id==db.group_rec.person_id)],
		groupby=db.groups.id,
		orderby=db.groups.name).as_list()

	groups = [dict((k[-1],v) for k,v in flattenDict(d).items()) for d in groups]
	
	return groups

def records(id):
	db = current.javelin.db
	result = db(db.group_rec.group_id==id).select(
		db.person.id, 
		db.person.last_name, 
		db.person.first_name, 
		join=db.person.on(db.person.id==db.group_rec.person_id)).as_list()
	
	return result

def add_group(name, description, values):
	db = current.javelin.db

	exists = not db(db.groups.name==name).isempty()

	if not exists:
		id = db.groups.insert(name=name, description=description)

		if values:
			rec_id = db.group_rec.bulk_insert([{'group_id' : id, 'person_id' : person_id} for person_id in values])
		else:
			rec_id = 0

		return dict(group_id=id, group_rec_id=rec_id)
	else:
		return dict(exists=True)

def add_to_group(person_id, group_id):
	db = current.javelin.db
	rec_id = db.group_rec.insert(person_id=person_id, group_id=group_id)

	return dict(group_rec_id=rec_id)

def delete_group(id):
	db = current.javelin.db
	deleted = db(db.groups.id==id).delete()
	
	return dict(deleted=deleted)

def delete_from_group(person_id, group_id):
	db = current.javelin.db
	deleted = db((db.group_rec.person_id==person_id) & (db.group_rec.group_id==group_id)).delete() # group_rec.delete().where(and_(group_rec.c.person_id==person_id, group_rec.c.group_id==group_id)).execute()
	
	return dict(deleted=deleted)

def edit_group(id, name, description):
	db = current.javelin.db
	exists = not db(db.groups.name==name).isempty()

	if not exists:
		response = db(db.groups.id==id).update(name=name, description=description)

		return dict(response=response)
	else:
		return dict(exists=True)

def get_people():
	db = current.javelin.db
	
	people = db().select(db.person.ALL).as_list() # people = person.select().execute().fetchall()

	result = []
	for p in people:
		result.append({'value' : str(p['id']), 'label' : p['last_name'] + ", " + p['first_name']})
	
	return result

def people_not_in_group(group_id, query):
	db = current.javelin.db

	people = [rec.person_id for rec in db(db.group_rec.group_id==group_id).select(db.group_rec.person_id)]

	if not query:
		return db(~(db.person.id.belongs(people)) & (db.person.leader==True)).select(
			db.person.id, db.person.last_name, db.person.first_name, orderby=db.person.last_name).as_list()
	else:
		people = db(~(db.person.id.belongs(people)) & 
			((db.person.last_name.contains(query)) | (db.person.first_name.contains(query))) &
			(db.person.leader==True) ).select(
			db.person.id, db.person.last_name, db.person.first_name, orderby=db.person.last_name).as_list()

		return people