# -*- coding: utf-8 -*-
"""
	Javelin Web2Py Admin Controller
"""

from applications.javelin.modules import modules_enabled, admin
from gluon.contrib import simplejson as json
from gluon.tools import Service
service = Service(globals())

@auth.requires_login()
@auth.requires_membership('admin')
def index():
	"""Loads the index page for the 'Admin' controller

	:returns: a dictionary to pass to the view with the list of modules_enabled and the active module ('admin')
	"""
	from applications.javelin.modules import get_module_data
	modules_data = get_module_data()
	users = db().select(db.auth_user.ALL)
	return dict(modules_enabled=modules_enabled, modules_data=modules_data, active_module='jadmin', users=users)

@auth.requires_login()
@auth.requires_membership('admin')
@service.json
def update_names(names):
	response = admin.update_names(json.loads(names))
	errors = list()
	for i in range(len(response)):
		if response[i] == 0:
			errors.append(names[i])

	return dict(errors=errors)

@auth.requires_login()
@auth.requires_membership('admin')
def call():
	"""Call function used when calling a function from an HTTP request"""
	return service()