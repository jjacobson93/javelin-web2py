# -*- coding: utf-8 -*-
"""
	Javelin Web2Py People Controller
"""

from applications.javelin.modules import modules_enabled, people

from gluon.tools import Service
service = Service(globals())

@auth.requires_login()
def index():
	return dict(modules_enabled=modules_enabled, active_module='people', form=people.load_form())

@auth.requires_login()
@service.json
def data(str_filter=None):
	return people.data(str_filter)

@auth.requires_login()
@service.json
def record(id):
	return people.record(id)

@auth.requires_login()
@service.json
def update_record():
	id = None
	values = {}
	for key in request.vars:
		if key == 'id':
			id = request.vars[key]
		else:
			values[key] = request.vars[key]

	return people.update_record(id, values)

@auth.requires_login()
@service.json
def update_pic(id, pic):
	return people.update_pic(id, pic)

@auth.requires_login()
def call():
    return service()