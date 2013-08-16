# -*- coding: utf-8 -*-
"""
	Javelin SB Web2Py Default Controller
"""

from gluon.storage import Storage
import datetime

@auth.requires_login()
def index():
	"""
	example action using the internationalization operator T and flash
	rendered by views/default/index.html or views/generic.html

	if you need a simple wiki simple replace the two lines below with:
	return auth.wiki()
	"""
	currdate = request.vars['date'] or request.now.date().strftime('%Y-%m-%d')
	return dict(dates=dates(), currdate=currdate)

@auth.requires_login()
def sections():
	date = request.vars['date']
	if not date or date == 'today':
		return dict(counts=counts())
	else:
		return dict(counts=counts(date))

@auth.requires_login()
def table():
	date = request.vars['date']
	section = request.vars['section_id']
	if not date or date == 'today':
		students = db(db.sb_att.event_date==request.now.date()).select(
				db.person.ALL, db.sb_att.ALL, 
				join=db.sb_att.on((db.person.id==db.sb_att.person_id) & (db.sb_att.sb_section_id==section)),
				orderby=[~db.sb_att.in_time, ~db.sb_att.out_time])
	else:
		students = db(db.sb_att.event_date==datetime.datetime.strptime(date, '%Y-%m-%d').date()).select(
				db.person.ALL, db.sb_att.ALL, 
				join=db.sb_att.on((db.person.id==db.sb_att.person_id) & (db.sb_att.sb_section_id==section)),
				orderby=[~db.sb_att.in_time, ~db.sb_att.out_time])

	return dict(students=students)

@auth.requires_login()
@service.json
def checkin(person_id, section_id, date):
	if type(date) == str:
		date = datetime.datetime.strptime(date, '%Y-%m-%d').date()

	student = db(db.person.student_id==person_id).select().first()
	if student:
		person_id = student.student_id

	check = db((db.sb_att.event_date==date) & 
		(db.sb_att.person_id==person_id) &
		(db.sb_att.sb_section_id==section_id)).select().first()

	result = None
	error = None
	if not check:
		checktwo = db((db.sb_att.person_id==person_id) & (db.sb_att.is_out==False)).select()
		if checktwo:
			for c in checktwo:
				update = db((db.sb_att.person_id==person_id) & 
					(db.sb_att.id==c.id)).update(studyhour=calc_hour(c.in_time), is_out=True) # if not checked out of other section, check out
		result = db.sb_att.insert(person_id=person_id, sb_section_id=section_id)
	else:
		result = 'Already exists'
		error = True

	return dict(response=result, error=error)

@auth.requires_login()
@service.json
def checkout(person_id, section_id, date):
	if type(date) == str:
		date = datetime.datetime.strptime(date, '%Y-%m-%d').date()

	student = db(db.person.student_id==person_id).select().first()
	if student:
		person_id = student.student_id

	check = db((db.sb_att.event_date==date) & 
		(db.sb_att.person_id==person_id) &
		(db.sb_att.sb_section_id==section_id)).select().first()
	result = None
	error = None
	if check:
		result = db(db.sb_att.id==check.id).update(studyhour=calc_hour(check.in_time), is_out=True)
	else:
		result = 'Does not exist'
		error = True

	return dict(response=result, error=error)

@auth.requires_login()
@service.json
def counts(date=request.now.date()):
	if type(date) is str:
		date = datetime.datetime.strptime(date, '%Y-%m-%d').date()

	sections= db().select(db.sb_section.ALL)
	counts = dict(('_'.join(s.title.lower().split()), db((db.sb_att.event_date==date) & 
		(db.sb_att.sb_section_id==s.id) & (db.sb_att.is_out==False)).count()) for s in sections)
	return counts

@auth.requires_login()
@service.json
def dates():
	dates = [dict(label=d.event_date.strftime('%B %d, %Y'), value=d.event_date.strftime('%Y-%m-%d'))
		for d in db().select(db.sb_att.event_date, groupby=db.sb_att.event_date)]
	return dates

def calc_hour(in_time):
	diff = request.now - in_time
	mins = divmod(diff.days * 86400 + diff.seconds, 60)[0]
	hours = mins*1.0/60.0
	if hours > 1.9 and hours < 3:
		hours = 2
	elif hours < 1.9 and hours > 0.9:
		hours = 1
	else:
		hours = 0
	return hours

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

	form = auth()
	if request.args(0)=='login':
		login_form = auth.login()
		form = FORM(
				FIELDSET(
					DIV(
						INPUT(_type='text', _name='username', 
							_id='auth_user_username', _placeholder="Username", 
							_class="form-control"),
						_class="form-group"
					),
					DIV(
						INPUT(_type='password', _name='password', 
							_id='auth_user_password', _placeholder="Password", _class="form-control"),
						_class="form-group"
					)
				),
				DIV(
					INPUT(_type='submit', _value="Login", _class='btn btn-primary btn-lg btn-block'),
					_class="form-group"
				),
				DIV(
					INPUT(_type='button', 
						_onclick="window.location='{}';return false".format(
							URL(args='register', vars={'_next': request.vars._next} 
								if request.vars._next else None)),
						_value='Register', _class='btn btn-default pull-left'),
					INPUT(_type='button', _onclick="window.location='{}';return false".format(URL(args='request_reset_password')),
						_value='Lost Password', _class='btn btn-default pull-right', _style='margin-right: 0'),
					_class="form-group"
				),
				_role="form"
			)
		form.append(login_form.custom.end)

		# if not 'register' in auth.settings.actions_disabled:
		# 	form.add_button(T('Register'),URL(args='register', vars={'_next': request.vars._next} if request.vars._next else None),_class='btn')

		# if not 'request_reset_password' in auth.settings.actions_disabled:
		# 	form.add_button(T('Lost Password'),URL(args='request_reset_password'),_class='btn')

	return dict(form=form)

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
