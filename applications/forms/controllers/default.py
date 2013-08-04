# -*- coding: utf-8 -*-
"""
	Javelin Bugs Web2Py Default Controller
"""

from gluon.tools import Service
service = Service(globals())

def index():
	"""
	example action using the internationalization operator T and flash
	rendered by views/default/index.html or views/generic.html

	if you need a simple wiki simple replace the two lines below with:
	return auth.wiki()
	"""
	forms = db().select(db.form.ALL)
	return dict(forms=forms)

def view():
	id = request.vars.id
	data = db(db.form.uuid==id).select(db.form.ALL).first()
	if data:
		form = SQLFORM(db[data.db_table])
		if form.process().accepted:
			response.flash = 'Form has been submitted!'
		elif form.errors:
			response.flash = 'There are errors in the form'
		return dict(form=form)
	else:
		return dict(form="Could not find form")

def verify():
	id = request.vars.id
	form = FORM(TR(
		LABEL('Verification Code:'), 
		INPUT(_name='verification', requires=IS_NOT_EMPTY())),
	INPUT(_type='submit'))

	if form.process().accepted:
		f = db(db.form.id==id).select().first()
		if f and form.vars.verification == f.verification_code:
			redirect(URL('view?id='+f.uuid))
		
		response.flash = "Verifcation code is incorrect"

	return dict(form=form)

@auth.requires_login()
@auth.requires_membership('admin')
def create_form():
	form = SQLFORM(db.form)
	if form.process().accepted:
		response.flash = 'Form accepted'
	elif form.errors:
		response.flash = 'There are errors in the form'
	return dict(form=form)

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