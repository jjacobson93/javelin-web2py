# -*- coding: utf-8 -*-
"""
	Javelin Web2Py Default Controller
"""

from applications.javelin.modules import modules_enabled, get_module_data

from gluon.tools import Service
service = Service(globals())

@auth.requires_login()
def index():
	"""
	example action using the internationalization operator T and flash
	rendered by views/default/index.html or views/generic.html

	if you need a simple wiki simple replace the two lines below with:
	return auth.wiki()
	"""
	modules_data = get_module_data()
	return dict(modules_enabled=modules_enabled, active_module='None', modules_data=modules_data)

@auth.requires_login()
def query():
	results = db((db.person.grade==9) & 
			(db.course.code.belongs('EN228', 'EN135', 'EN137'))).select(
		db.person.id, db.person.crew, db.course.title, db.teacher.teacher_name, db.course.period,
		left=[db.course_rec.on(db.person.id==db.course_rec.student_id),
			db.course.on(db.course.id==db.course_rec.course_id),
			db.teacher.on(db.teacher.id==db.course.teacher_id)],
		orderby=[db.person.crew, db.person.id])
	return dict(results=results)

def user():
	"""
	exposes:
	http://..../[app]/default/user/login
	http://..../[app]/default/user/logout
	http://..../[app]/default/user/register
	http://..../[app]/default/user/profile
	http://..../[app]/default/user/retrieve_password
	http://..../[app]/default/user/change_password
	http://..../[app]/default/user/manage_users (requires membership in 
	use @auth.requires_login()
		@auth.requires_membership('group name')
		@auth.requires_permission('read','table name',record_id)
	to decorate functions that need access control
	"""
	return dict(form=auth())

@auth.requires_login()
@cache.action()
def download():
	"""
	allows downloading of uploaded files
	http://..../[app]/default/download/[filename]
	"""
	return response.download(request, db)

@auth.requires_login()
def call():
	"""
	exposes services. for example:
	http://..../[app]/default/call/jsonrpc
	decorate with @services.jsonrpc the functions to expose
	supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
	"""
	return service()

@auth.requires_signature()
def data():
	"""
	http://..../[app]/default/data/tables
	http://..../[app]/default/data/create/[table]
	http://..../[app]/default/data/read/[table]/[id]
	http://..../[app]/default/data/update/[table]/[id]
	http://..../[app]/default/data/delete/[table]/[id]
	http://..../[app]/default/data/select/[table]
	http://..../[app]/default/data/search/[table]
	but URLs must be signed, i.e. linked with
	  A('table',_href=URL('data/tables',user_signature=True))
	or with the signed load operator
	  LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
	"""
	return dict(form=crud())