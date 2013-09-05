# -*- coding: utf-8 -*-
"""
	Javelin SB Web2Py Tutors Controller
"""

from gluon.storage import Storage
import datetime

@auth.requires_login()
def index():
	return dict()

@auth.requires_login()
def table():
	start = request.vars.get('start', None)
	end = request.vars.get('end', None)

	section = request.vars['section_id']
	if start and end:
		start = datetime.datetime.strptime(start, '%Y-%m-%d-%H-%M-%S')
		end = datetime.datetime.strptime(end, '%Y-%m-%d-%H-%M-%S')
		mid = start + ((end - start)/2)
		weekday = mid.weekday()
		weekdaynames = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
		semester = season(start.month)
		
		records = db().select(db.person.ALL, db.study_buddy.ALL,
				join=db.study_buddy.on(db.person.id==db.study_buddy.person_id),
				orderby=db.person.last_name|db.person.first_name)

		records = [s for s in records

		if (	
				(
					not s.study_buddy.days=='Both' and s.study_buddy.days == weekdaynames[weekday]
				)
					or
				(
					(weekday==1 or weekday==3) and s.study_buddy.days=='Both'
				)
					or
				(
					s.study_buddy.lunch=='Yes' and (weekday==0 or weekday==2 or weekday==4)
				)
			)
				and
			(
				(s.study_buddy.semester == 'Both')
					or 
				(s.study_buddy.semester != 'Both' and semester == s.study_buddy.semester)
			)
		]

		def recordsfor(id):
			return db(((db.sb_att.in_time >= start) & 
				(db.sb_att.in_time < end))).select(
				db.person.ALL, db.sb_att.ALL, db.sb_section.ALL,
				join=[db.sb_att.on((db.person.id==db.sb_att.person_id) & (db.person.id==id)),
					db.sb_section.on(db.sb_section.id==db.sb_att.sb_section_id)],
				orderby=db.person.last_name|db.person.first_name)

		students = list()
		for p in records:
			s = Storage(subjects=[],totalhours=[], in_time=None, out_time=None, is_out=True, **dict((c,v) for c, v in p.items()))
			rfor = recordsfor(p.person.id)
			for r in rfor:
				s.subjects.append(str(r.sb_section.title))
				s.totalhours.append(r.sb_att.studyhour)
				if not s.in_time or (r.sb_att.in_time and r.sb_att.in_time < s.in_time):
					s.in_time = r.sb_att.in_time

				if not s.out_time or (r.sb_att.out_time and r.sb_att.out_time > s.out_time):
					s.out_time = r.sb_att.out_time

				if s.is_out == True and r.sb_att.is_out == False:
					s.is_out = False

			s.subjects = ', '.join(s.subjects)
			s.totalhours = sum(s.totalhours) if sum(s.totalhours) <= 2 else 2

			students.append(s)

		return dict(students=students, semester=semester, weekday=weekday)
	else:
		return dict(students=list())

def season(month):
	if month >= 1 and month <= 6:
		return 'Spring'
	elif month >= 8 and month <= 12:
		return 'Fall'
	else:
		return 'Summer'

@auth.requires_login()
def signup():
	form = SQLFORM(db.study_buddy, formstyle="divs")
	if form.process(onvalidation=add_to_group).accepted:
		response.flash = 'Form has been submitted!'
	elif form.errors:
		response.flash = 'There are errors in the form'
	return dict(form=form)

@auth.requires_login()
def edit_tutor():
	tutor_id = request.vars.get('tutor_id', None)
	if tutor_id:
		db.study_buddy.id.readable = False
		db.study_buddy.person_id.writable = False
		db.study_buddy.person_id.represent = lambda row: ', '.join([row.last_name, row.first_name])

		form = SQLFORM(db.study_buddy, tutor_id, formstyle="divs")
		if form.process(onvalidation=add_to_group, next=URL(a='studybuddies', c='tutors', f='all')).accepted:
			response.flash = 'Form has been submitted!'
		elif form.errors:
			response.flash = 'There are errors in the form'
		return dict(form=form)
	else:
		return dict(form="ERROR")

@auth.requires_login()
def all():
	tutors = db().select(db.person.id, db.person.student_id, db.person.last_name, 
			db.person.first_name, db.person.grade, db.study_buddy.ALL,
		join=db.study_buddy.on(db.person.id==db.study_buddy.person_id),
		orderby=db.person.last_name|db.person.first_name)

	return dict(tutors=tutors)

@auth.requires_login()
def archive():
	currdate = request.now.strftime('%Y-%m-%d-%H-%M-%S')
	return dict(currdate=currdate)

@auth.requires_login()
def add_to_group(form):
	group = db(db.groups.name.like('%tutor%')).select(db.groups.id).first()
	if group:
		db.group_rec.insert(group_id=group.id, person_id=form.vars.person_id)
