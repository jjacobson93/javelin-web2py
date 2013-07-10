# -*- coding: utf-8 -*-
"""
	Javelin Web2Py People Controller
"""

from applications.javelin.modules import modules_enabled
from applications.javelin.modules import people

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

def call():
    return service()