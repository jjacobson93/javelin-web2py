# -*- coding: utf-8 -*-
"""
	Javelin Web2Py Groups Controller
"""

from applications.javelin.modules import modules_enabled, modules_data, groups

from gluon.tools import Service
service = Service(globals())

@auth.requires_login()
def index():
	return dict(modules_enabled=modules_enabled, active_module='groups', labels=modules_data['groups']['labels'])

@auth.requires_login()
@service.json
def data():
	return groups.data()

@auth.requires_login()
@service.json
def records(id):
	return groups.records(id)

@auth.requires_login()
@service.json
def add_group(name, description, values):
	return groups.add_group(name, description, values)

@auth.requires_login()
@service.json
def add_to_group(person_id, group_id):
	return groups.add_to_group(person_id, group_id)

@auth.requires_login()
@service.json
def delete_group(id):
	return groups.delete_group(id)

@auth.requires_login()
@service.json
def delete_from_group(person_id, group_id):		
	return groups.delete_from_group(person_id, group_id)

@auth.requires_login()
@service.json
def edit_group(id, name, description):
	return groups.edit_group(id, name, description)

@auth.requires_login()
@service.json
def get_people():
	return groups.get_people()

@auth.requires_login()
def call():
    return service()