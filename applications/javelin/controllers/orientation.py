# -*- coding: utf-8 -*-
"""
	Javelin Web2Py Orientation Controller
"""

from applications.javelin.modules import modules_enabled, get_module_data, orientation
from gluon.contrib import simplejson as json
from gluon.tools import Service
service = Service(globals())

@auth.requires_login()
def index():
	"""Loads the index page for the 'Orientation' controller

	:returns: a dictionary to pass to the view with the list of modules_enabled and the active module ('orientation')
	"""
	modules_data = get_module_data()
	existing_nametags = db().select(db.file.ALL)
	return dict(modules_enabled=modules_enabled, modules_data=modules_data, active_module='orientation', existing_nametags=existing_nametags)

@auth.requires_login()
@service.json
def attendance_data(event_id):
	return orientation.attendance_data(event_id)

@auth.requires_login()
@service.json
def quick_attendance(person_id, event_id, present=True):
	return orientation.quick_attendance(person_id, event_id, present)

@auth.requires_login()
@service.json
def make_labels(event_name, type, filename='labels'):
	return orientation.make_labels(event_name, type, filename)

@auth.requires_login()
@service.json
def crews():
	return orientation.crews()

@auth.requires_login()
@service.json
def crew_records(id):
	return orientation.crew_records(id)

@auth.requires_login()
@service.json
def add_crew(room, wefsk, people):
	return orientation.add_crew(room, wefsk, json.loads(people))

@auth.requires_login()
@service.json
def people_not_in_crew(id, query):
	return orientation.people_not_in_crew(id, query)

@auth.requires_login()
@service.json
def add_people_to_crew(id, people):
	return orientation.add_people_to_crew(id, json.loads(people))

@auth.requires_login()
def call():
	"""Call function used when calling a function from an HTTP request"""
	return service()