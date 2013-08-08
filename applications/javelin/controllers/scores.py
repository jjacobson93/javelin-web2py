# -*- coding: utf-8 -*-
"""
	Javelin Web2Py Scores Controller
"""

from applications.javelin.modules import modules_enabled, get_module_data, scores
from gluon.contrib import simplejson as json
from gluon.tools import Service
service = Service(globals())

@auth.requires_login()
@auth.requires_membership('standard')
def index():
	"""Loads the index page for the 'Scores' controller

	:returns: a dictionary to pass to the view with the list of modules_enabled, the active module ('scores') and a dynamic form
	"""
	modules_data = get_module_data()
	return dict(modules_enabled=modules_enabled, active_module='scores', modules_data=modules_data, crews=data())

@auth.requires_login()
@auth.requires_membership('standard')
def table():
	return dict(crews=data())

@auth.requires_login()
@auth.requires_membership('standard')
@service.json
def data():
	result = [dict([('id',id), 
			('leaders', ', '.join(leaders) if leaders[-1] is not None else 'No Leaders'), 
			('score', score if score else 'None')]) 
		for id, leaders, score in
		db.executesql("SELECT crew.id, array_agg(person.first_name || ' ' || person.last_name) " +\
		"AS leaders, score.score FROM crew LEFT JOIN person ON person.crew = crew.id " +\
		"AND person.leader = 'T' " +\
		"LEFT JOIN score ON score.crew_id = crew.id " +\
		"GROUP BY crew.id, score.score ORDER BY crew.id;")]
	return result

@auth.requires_login()
@auth.requires_membership('standard')
@service.json
def update_score(id, score):
	response = db.score.update_or_insert(db.score.crew_id==id, crew_id=id, score=score)
	return dict(response=response)

@auth.requires_login()
@auth.requires_membership('standard')
def call():
	"""Call function used when calling a function from an HTTP request"""
	return service()