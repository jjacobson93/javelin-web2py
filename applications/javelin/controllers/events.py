# -*- coding: utf-8 -*-
"""
	Javelin Web2Py Events Controller
"""

from applications.javelin.modules import modules_enabled, get_module_data, events
from gluon.contrib import simplejson as json
from gluon.tools import Service
service = Service(globals())

@auth.requires_login()
@auth.requires_membership('standard')
def index():
	"""Loads the index page for the 'Events' controller

	:returns: a dictionary to pass to the view with the list of modules_enabled and the active module ('events')
	"""
	modules_data = get_module_data()
	return dict(modules_enabled=modules_enabled, modules_data=modules_data, active_module='events')

@auth.requires_login()
@auth.requires_membership('standard')
@service.json
def data(start=None, end=None, _=None):
	"""Loads the event data

	:param start: the start time
	:param end: the end time
	:returns: a list of events between the start and end times
	"""
	return events.data(start, end)

@auth.requires_login()
@auth.requires_membership('standard')
@service.json
def add_event(title, start, end, notes=None, allDay=False, recurring=False, end_recur=None):
	"""Adds an event

	:param title: the title for the event
	:param start: start time for the event
	:param end: end time for the event
	:param notes: notes for the event
	:returns: a dictionary with a response of success or failure
	"""
	return events.add_event(title, start, end, notes, allDay, recurring, end_recur)

@auth.requires_login()
@auth.requires_membership('standard')
@service.json
def delete_event(id):
	"""Deletes an event

	:param id: the id of the event
	:returns: a dictionary with a response of success or failure
	"""
	return events.delete_event(id)

@auth.requires_login()
@auth.requires_membership('standard')
def call():
	"""Call function used when calling a function from an HTTP request"""
	return service()