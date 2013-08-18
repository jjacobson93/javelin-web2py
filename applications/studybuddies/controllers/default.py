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
	currdate = request.now.strftime('%Y-%m-%d-%H-%M-%S') #this is UTC time
	return dict(currdate=currdate)

@auth.requires_login()
def sections():
	start = request.vars.get('start', None)
	end = request.vars.get('end', None)
	if start and end:
		return dict(counts=counts(start, end))
	else:
		return dict(counts=dict())
		

@auth.requires_login()
def table():
	start = request.vars.get('start', None)
	end = request.vars.get('end', None)

	section = request.vars['section_id']
	if start and end:
		start = datetime.datetime.strptime(start, '%Y-%m-%d-%H-%M-%S')
		end = datetime.datetime.strptime(end, '%Y-%m-%d-%H-%M-%S')
		
		students = db(((db.sb_att.in_time >= start) & (db.sb_att.in_time < end)) |
			((db.sb_att.out_time >= start) & (db.sb_att.out_time < end)) ).select(
				db.person.ALL, db.sb_att.ALL, 
				join=db.sb_att.on((db.person.id==db.sb_att.person_id) & (db.sb_att.sb_section_id==section)),
				orderby=[~db.sb_att.in_time, ~db.sb_att.out_time])

		return dict(students=students)
	else:
		return dict(students=list())

@auth.requires_login()
@service.json
def checkin(person_id, section_id):
	student = db((db.person.student_id==person_id) | 
		(db.person.id==person_id)).select().first()
	result = None
	error = None

	if student:
		person_id = student.id

		check = db((db.sb_att.is_out==False) & 
			(db.sb_att.person_id==person_id) &
			(db.sb_att.sb_section_id==section_id)).select().first()

		
		if not check:
			checktwo = db((db.sb_att.person_id==person_id) & 
				(db.sb_att.is_out==False)).select()
			if checktwo:
				for c in checktwo:
					update = db((db.sb_att.person_id==person_id) & 
						(db.sb_att.id==c.id)).update(studyhour=calc_hour(c.in_time), is_out=True) # if not checked out of other section, check out
			result = db.sb_att.insert(person_id=person_id, sb_section_id=section_id)
		else:
			result = 'Already exists'
			error = True
	else:
		result = "No person exists with ID"
		error = True

	return dict(response=result, error=error)

@auth.requires_login()
@service.json
def checkout(person_id):
	student = db((db.person.student_id==person_id) | 
		(db.person.id==person_id)).select().first()
	result = None
	error = None

	if student:
		person_id = student.id

		check = db((db.sb_att.is_out==False) &
					(db.sb_att.person_id==person_id)).select()
		if check:
			for c in check:
				db(db.sb_att.id==c.id).update(studyhour=calc_hour(c.in_time), is_out=True)
		else:
			result = 'Does not exist'
			error = True
	else:
		result = "No person exists with ID"
		error = True

	return dict(response=result, error=error)

@auth.requires_login()
def checkoutall():
	currdate = request.now.strftime('%Y-%m-%d-%H-%M-%S') #this is UTC time
	return dict(currdate=currdate)

@auth.requires_login()
def checkout_table():
	start = request.vars.get('start', None)
	end = request.vars.get('end', None)

	if start and end:
		start = datetime.datetime.strptime(start, '%Y-%m-%d-%H-%M-%S')
		end = datetime.datetime.strptime(end, '%Y-%m-%d-%H-%M-%S')

		records = db(((db.sb_att.in_time >= start) & 
			(db.sb_att.in_time < end)) &
			(db.sb_att.is_out==True)).select(
				db.person.ALL, db.sb_att.ALL, db.sb_section.ALL,
				join=[db.sb_att.on(db.person.id==db.sb_att.person_id),
					db.sb_section.on(db.sb_section.id==db.sb_att.sb_section_id)],
				orderby=db.person.id|db.person.last_name|db.person.first_name,
				distinct=db.person.id)

		def recordsfor(id):
			return db(((db.sb_att.in_time >= start) & 
				(db.sb_att.in_time < end)) &
			(db.sb_att.is_out==True)).select(
				db.person.ALL, db.sb_att.ALL, db.sb_section.ALL,
				join=[db.sb_att.on((db.person.id==db.sb_att.person_id) & (db.person.id==id)),
					db.sb_section.on(db.sb_section.id==db.sb_att.sb_section_id)],
				orderby=[db.person.last_name, db.person.first_name])

		students = list()
		for p in records:
			s = Storage(subjects=[],totalhours=[], in_time=None, out_time=None, **dict((c,v) for c, v in p.items()))
			for r in recordsfor(p.person.id):
				s.subjects.append(str(r.sb_section.title))
				s.totalhours.append(r.sb_att.studyhour)
				if not s.in_time or (r.sb_att.in_time and r.sb_att.in_time < s.in_time):
					s.in_time = r.sb_att.in_time

				if not s.out_time or (r.sb_att.out_time and r.sb_att.out_time > s.out_time):
					s.out_time = r.sb_att.out_time

			s.subjects = ', '.join(s.subjects)
			s.totalhours = sum(s.totalhours) if sum(s.totalhours) <= 2 else 2

			students.append(s)


		return dict(students=students)

	return dict(students=list())

@auth.requires_login()
@service.json
def checkout_any(person_id):
	student = db((db.person.student_id==person_id) | 
		(db.person.person_id==person_id)).select().first()
	result = None
	error = None

	if student:
		person_id = student.student_id

		check = db((db.sb_att.is_out==False) & 
			(db.sb_att.person_id==person_id)).select().first()
		
		if check:
			result = db(db.sb_att.id==check.id).update(studyhour=calc_hour(check.in_time), is_out=True)
	else:
		result = "No person exists with ID"
		error = True

	return dict(response=result, error=error)

@auth.requires_login()
@service.json
def counts(start, end):
	if start and end:
		start = datetime.datetime.strptime(start, '%Y-%m-%d-%H-%M-%S')
		end = datetime.datetime.strptime(end, '%Y-%m-%d-%H-%M-%S')

		sections = db().select(db.sb_section.ALL)
		counts = dict(('_'.join(s.title.lower().split()), 
			db( (((db.sb_att.in_time >= start) & (db.sb_att.in_time < end)) |
				((db.sb_att.out_time >= start) & (db.sb_att.out_time < end))) & 
				(db.sb_att.sb_section_id==s.id) & 
				(db.sb_att.is_out==False)).count()) for s in sections)
		return counts
	else:
		return dict()

# @auth.requires_login()
# @service.json
# def dates(offset):
# 	"""
# 		:param offset: Timezone offset in minutes
# 	"""
# 	minimum = db.sb_att.in_time.min()
# 	earliest = db().select(minimum).first()
	
# 	dates = list()
# 	if earliest:
# 		now = request.now
# 		numdays = (now - earliest).days
# 		for x in range(numdays):
# 			new = earliest - datetime.timedelta(minutes=offset) + datetime.timedelta(days=x)
# 			dates.append(dict(label=new.strftime('%B %d, %Y'), value=new.strftime('%Y-%m-%d-%H-%M-%S')))
# 	else:
# 		new = now - datetime.timedelta(minutes=offset)
# 		dates.append(dict(label=new.strftime('%B %d, %Y'), value=new.strftime('%Y-%m-%d-%H-%M-%S')))

# 	return dates

def is_in_day(time, date):
	start = datetime.datetime(date.year, date.month, date.day)
	end = start + datetime.timedelta(1)
	return True if (time >= start and time < end) else False

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
