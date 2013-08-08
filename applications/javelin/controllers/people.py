# -*- coding: utf-8 -*-
"""
	Javelin Web2Py People Controller
"""

from applications.javelin.modules import modules_enabled, get_module_data, people
from gluon.contrib import simplejson as json
from gluon.tools import Service
service = Service(globals())

@auth.requires_login()
@auth.requires_membership('standard')
def index():
	"""Loads the index page for the 'People' controller

	:returns: a dictionary to pass to the view with the list of modules_enabled, the active module ('people') and a dynamic form
	"""
	modules_data = get_module_data()
	return dict(modules_enabled=modules_enabled, active_module='people', modules_data=modules_data)

@auth.requires_login()
@auth.requires_membership('standard')
@service.json
def data(str_filter=None):
	"""Loads the data for people with an optional filter

	:param str_filter: an optional string filter
	:returns: a list of people
	"""
	return people.data(str_filter)

@auth.requires_login()
@auth.requires_membership('standard')
@service.json
def leaders(query=None):
	"""Loads the data for people who are a leader

	:param query: an optional string filter
	:returns: a list of people
	"""
	return people.leaders(query)

@auth.requires_login()
@auth.requires_membership('standard')
@service.json
def record(id):
	"""Loads a single record

	:param id: the id of the record to be returned
	:returns: a record dictionary of a person
	"""
	return people.record(id)

@auth.requires_login()
@auth.requires_membership('standard')
@service.json
def update_record(id, values):
	"""Updates a record

	:param id: the id of the record
	:returns: a dictionary with a response, either a 0 or 1, depending on success
	"""
	return people.update_record(id, json.loads(values))

@auth.requires_login()
@auth.requires_membership('standard')
@service.json
def update_pic(id, pic):
	"""Updates a picture on a record

	:param id: the id of the record
	:param pic: the picture in base64 encoding
	:returns: a dictionary with a response, either a 0 or 1, depending on success
	"""
	return people.update_pic(id, pic)

@auth.requires_login()
@auth.requires_membership('standard')
def call():
	"""Call function used when calling a function from an HTTP request"""
	return service()