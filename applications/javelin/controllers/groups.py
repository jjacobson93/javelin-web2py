# -*- coding: utf-8 -*-
"""
	Javelin Web2Py Groups Controller
"""

# metadata
__author__ = "Jeremy Jacobson"
__copyright__ = "(c) 2013, Jacobson and Varni, LLC"
__date__ = "7/9/2013"
__email__ = "jjacobson93@gmail.com"
__data__ = {'name' : 'groups', 'label' : 'Groups', 'description' : 'Create groups and add people to them', 
	'icon' : 'book', 'u-icon' : u'\uf02d', 'color': 'green', 'required' : True}

from applications.javelin.ctr_data import ctr_enabled, get_ctr_data
from applications.javelin.private.utils import flattenDict
from gluon.contrib import simplejson as json

from gluon.tools import Service
service = Service(globals())

import logging
logger = logging.getLogger('web2py.app.javelin')

@auth.requires_login()
@auth.requires_membership('standard')
def index():
	"""Loads the index page for the 'Groups' controller

	:returns: a dictionary to pass to the view with the list of modules_enabled, the active module ('groups') and the labels for 'groups'
	"""
	ctr_data = get_ctr_data()
	return dict(ctr_enabled=ctr_enabled, active_module='groups', labels=ctr_data['groups']['labels'], ctr_data=ctr_data)

@auth.requires_login()
@auth.requires_membership('standard')
@service.json
def data():
	"""Loads the data for groups

	:returns: a list of groups
	"""
	count = db.person.id.count()
	groups = db().select(
		db.groups.ALL, count.with_alias('count'),
		left=[db.group_rec.on(db.groups.id==db.group_rec.group_id), 
			db.person.on(db.person.id==db.group_rec.person_id)],
		groupby=db.groups.id,
		orderby=db.groups.name).as_list()

	groups = [dict([('actions', '<button class="btn btn-xs btn-primary" id="edit-row-' + str(d['groups']['id']) + '">' +\
						'<i class="icon-edit"></i>Edit' + '</button>' +\
					'<button class="btn btn-xs btn-danger" id="delete-row-' + str(d['groups']['id']) + '" style="margin-left: 10px">' +\
						'<i class="icon-trash"></i>Delete' + \
					'</button>')] + [(k[-1],v) for k,v in flattenDict(d).items()]) for d in groups]
	
	return groups

@auth.requires_login()
@auth.requires_membership('standard')
@service.json
def records(id):
	"""Loads the records for the group

	:param id: the id of the group
	:returns: a list of records for the group
	"""
	result = db(db.group_rec.group_id==id).select(
		db.person.id, 
		db.person.last_name, 
		db.person.first_name, 
		join=db.person.on(db.person.id==db.group_rec.person_id),
		orderby=db.person.last_name|db.person.first_name).as_list()

	result = [dict([('actions',
						'<button class="btn btn-xs btn-danger" id="delete-row-' + str(d['id']) + '" style="margin-left: 10px">' +\
						'<i class="icon-trash"></i>Delete</button>')] + [(k,v) for k,v in d.items()]) for d in result]
	
	return result

@auth.requires_login()
@auth.requires_membership('standard')
@service.json
def add_group(name, description, values): 
	"""Adds a group

	:param name: the name of the group
	:param description: the description of the group
	:param values: a list of people to be added to the group
	:returns: the id of the added group and ids for the records for the group or
	 a boolean true value if the name already exists
	"""
	values = json.loads(values)

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

@auth.requires_login()
@auth.requires_membership('standard')
@service.json
def add_to_group(group_id, person_id=0, people=None, multiple=False):
	"""Adds a person to the group

	:param person_id: the id of the person
	:param group_id: the id of the group
	:returns: a dictionary with the id of the record for the group
	"""
	if multiple and people:
		people = json.loads(people)
		response = list()
		for person_id in people:
			rec_id = db.group_rec.insert(person_id=person_id, group_id=group_id)
			response.append(dict(group_rec_id=rec_id))
		return dict(response=response)
	else:
		rec_id = db.group_rec.insert(person_id=person_id, group_id=group_id)

		return dict(group_rec_id=rec_id)

@auth.requires_login()
@auth.requires_membership('standard')
@service.json
def delete_group(id):
	"""Deletes a group

	:param id: the id of the group
	:returns: a dictionary with a response, either a 0 or 1, depending on success
	""" 
	deleted = db(db.groups.id==id).delete()
	
	return dict(deleted=deleted)

@auth.requires_login()
@auth.requires_membership('standard')
@service.json
def delete_from_group(person_id, group_id):	
	"""Deletes a person from the group

	:param person_id: the id of the person
	:param group_id: the id of the group
	:returns: a dictionary with a response, either a 0 or 1, depending on success
	"""
	deleted = db((db.group_rec.person_id==person_id) & (db.group_rec.group_id==group_id)).delete()
	
	return dict(deleted=deleted)

@auth.requires_login()
@auth.requires_membership('standard')
@service.json
def edit_group(id, name, description):
	"""Edits a group

	:param id: the id of the group
	:param name: the name of the group
	:param description: the description of the group
	:returns: a dictionary with a response, either a 0 or 1, depending on success or
	 a boolean true value if the name already exists
	""" 
	exists = not db(db.groups.name==name).isempty()

	if not exists:
		response = db(db.groups.id==id).update(name=name, description=description)

		return dict(response=response)
	else:
		return dict(exists=True)

@auth.requires_login()
@auth.requires_membership('standard')
@service.json
def get_people():
	"""Gets a list of people

	:returns: a list of people
	"""
	people = db().select(db.person.ALL).as_list() # people = person.select().execute().fetchall()

	result = []
	for p in people:
		result.append({'value' : str(p['id']), 'label' : p['last_name'] + ", " + p['first_name']})
	
	return result

@auth.requires_login()
@auth.requires_membership('standard')
@service.json
def people_not_in_group(group_id, query):
	"""Gets a list of people not in a group

	:returns: a list of people
	"""
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

@auth.requires_login()
@auth.requires_membership('standard')
def call():
	"""Call function used when calling a function from an HTTP request"""
	return service()