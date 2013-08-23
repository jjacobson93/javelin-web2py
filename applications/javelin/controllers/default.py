# -*- coding: utf-8 -*-
"""
	Javelin Web2Py Default Controller
"""

from applications.javelin.modules import modules_enabled, get_module_data

from gluon.tools import Service
service = Service(globals())

@auth.requires_login()
@auth.requires_membership('standard')
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
@auth.requires_membership('standard')
def query():
	results = db((db.person.grade==9) & 
			(db.course.code.belongs('EN228', 'EN135', 'EN137'))).select(
		db.person.id, db.person.crew, db.course.title, db.teacher.teacher_name, db.course.period,
		left=[db.course_rec.on(db.person.id==db.course_rec.student_id),
			db.course.on(db.course.id==db.course_rec.course_id),
			db.teacher.on(db.teacher.id==db.course.teacher_id)],
		orderby=[db.person.crew, db.person.id])
	return dict(results=results)

@auth.requires_login()
@auth.requires_membership('standard')
def javelin_header():
	header = 'Vintage Crusher Crew'
	recipient = 'Jeremy'
	content = """Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed vulputate mauris sollicitudin felis mollis, sit amet porta ante laoreet. Aliquam erat volutpat. Ut dapibus magna sed nulla hendrerit ullamcorper. Aliquam sapien neque, ullamcorper sed sem lacinia, auctor ullamcorper quam. Aenean eget tellus eget justo consectetur elementum. Aliquam interdum gravida eros, pretium congue enim sagittis eget. Proin quis felis urna. Aliquam congue neque odio, sed tristique sem commodo vulputate. Donec eleifend tempor metus ac lacinia. Sed egestas vel arcu non pellentesque. Aliquam ac viverra purus. Cras vehicula lectus ut nibh ornare hendrerit. Morbi ornare congue urna, sed imperdiet tortor viverra at. Praesent dapibus turpis neque, ut suscipit nunc consequat non.\n
				Mauris laoreet tristique dui sit amet blandit. Fusce tempus euismod nibh id ultrices. Nunc in enim ac justo vehicula pulvinar. Phasellus ultricies ac turpis id aliquam. Donec scelerisque massa eget malesuada fringilla. Curabitur nec congue est. Vestibulum volutpat dui eget sem auctor, id suscipit nunc dapibus. Etiam vulputate ac lorem nec tristique. Morbi a eros vitae lectus sodales venenatis. Integer pretium nisl nec arcu porta, nec cursus tortor porta. Quisque semper quis augue nec luctus. Suspendisse sed vehicula erat, a tempor quam. Donec sollicitudin molestie erat vel lacinia. Suspendisse porta ipsum vitae venenatis adipiscing. Nam blandit urna eget metus semper vulputate. Integer vel turpis condimentum, auctor diam et, pellentesque dolor."""
	content = content.split('\n')
	return dict(header=header, recipient=recipient, content=content)

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
@auth.requires_membership('standard')
@cache.action()
def download():
	"""
	allows downloading of uploaded files
	http://..../[app]/default/download/[filename]
	"""
	return response.download(request, db)

@auth.requires_login()
@auth.requires_membership('standard')
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