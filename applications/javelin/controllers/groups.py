# -*- coding: utf-8 -*-
"""
	Javelin Web2Py Groups Controller
"""

from applications.javelin.modules import modules_enabled, get_module_data, groups
from gluon.contrib import simplejson as json

from gluon.tools import Service
service = Service(globals())

import logging
logger = logging.getLogger('web2py.app.javelin')

@auth.requires_login()
def index():
	"""Loads the index page for the 'Groups' controller

	:returns: a dictionary to pass to the view with the list of modules_enabled, the active module ('groups') and the labels for 'groups'
	"""
	modules_data = get_module_data()
	return dict(modules_enabled=modules_enabled, active_module='groups', labels=modules_data['groups']['labels'], modules_data=modules_data)

@auth.requires_login()
@service.json
def data():
	"""Loads the data for groups

	:returns: a list of groups
	"""
	return groups.data()

@auth.requires_login()
@service.json
def records(id):
	"""Loads the records for the group

	:param id: the id of the group
	:returns: a list of records for the group
	"""
	return groups.records(id)

@auth.requires_login()
@service.json
def add_group(name, description, values): 
	"""Adds a group

	:param name: the name of the group
	:param description: the description of the group
	:param values: a list of people to be added to the group
	:returns: the id of the added group and ids for the records for the group or
	 a boolean true value if the name already exists
	"""
	return groups.add_group(name, description, json.loads(values))

@auth.requires_login()
@service.json
def add_to_group(person_id, group_id):
	"""Adds a person to the group

	:param person_id: the id of the person
	:param group_id: the id of the group
	:returns: a dictionary with the id of the record for the group
	"""
	return groups.add_to_group(person_id, group_id)

@auth.requires_login()
@service.json
def delete_group(id):
	"""Deletes a group

	:param id: the id of the group
	:returns: a dictionary with a response, either a 0 or 1, depending on success
	""" 
	return groups.delete_group(id)

@auth.requires_login()
@service.json
def delete_from_group(person_id, group_id):	
	"""Deletes a person from the group

	:param person_id: the id of the person
	:param group_id: the id of the group
	:returns: a dictionary with a response, either a 0 or 1, depending on success
	"""
	return groups.delete_from_group(person_id, group_id)

@auth.requires_login()
@service.json
def edit_group(id, name, description):
	"""Edits a group

	:param id: the id of the group
	:param name: the name of the group
	:param description: the description of the group
	:returns: a dictionary with a response, either a 0 or 1, depending on success or
	 a boolean true value if the name already exists
	""" 
	return groups.edit_group(id, name, description)

@auth.requires_login()
@service.json
def get_people():
	"""Gets a list of people

	:returns: a list of people
	"""
	return groups.get_people()

@auth.requires_login()
def call():
	"""Call function used when calling a function from an HTTP request"""
	return service()