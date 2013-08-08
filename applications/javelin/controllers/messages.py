# -*- coding: utf-8 -*-
"""
	Javelin Web2Py Messages Controller
"""

from applications.javelin.modules import modules_enabled, get_module_data, messages
from gluon.contrib import simplejson as json
from gluon.tools import Service
service = Service(globals())

@auth.requires_login()
@auth.requires_membership('standard')
def index():
	"""Loads the index page for the 'Messages' controller

	:returns: a dictionary to pass to the view with the list of modules_enabled and the active module ('messages')
	"""
	modules_data = get_module_data()
	return dict(modules_enabled=modules_enabled, modules_data=modules_data, active_module='messages')

@auth.requires_login()
@auth.requires_membership('standard')
@service.json
def send_sms(message, to='all_leaders'):
	return messages.send_sms(message, to)

@auth.requires_login()
@auth.requires_membership('standard')
@service.json
def get_recipients(query=None):
	return messages.get_recipients(query)

@auth.requires_login()
@auth.requires_membership('standard')
def call():
	"""Call function used when calling a function from an HTTP request"""
	return service()