# -*- coding: utf-8 -*-
"""
	Javelin SB Web2Py Archive Controller
"""

from gluon.storage import Storage

@auth.requires_login()
def index():
	currdate = request.vars['date'] or request.now.date().strftime('%Y-%m-%d')
	return dict(dates=dates(), currdate=currdate)

@auth.requires_login()
def table():
	date = request.vars['date'] or request.now.date().strftime('%Y-%m-%d')
	date = datetime.datetime.strptime(date, '%Y-%m-%d').date()

	if date == 'today':
		date = request.now.date()

	records = db(db.sb_att.event_date==date).select(
			db.person.ALL, db.sb_att.ALL, db.sb_section.ALL,
			join=[db.sb_att.on(db.person.id==db.sb_att.person_id),
				db.sb_section.on(db.sb_section.id==db.sb_att.sb_section_id)],
			orderby=[db.person.last_name, db.person.first_name],
			groupby=[db.person.id])

	def recordsfor(id):
		return db(db.sb_att.event_date==date).select(
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

@auth.requires_login()
@service.json
def dates():
	dates = [dict(label=d.event_date.strftime('%B %d, %Y'), value=d.event_date.strftime('%Y-%m-%d'))
		for d in db().select(db.sb_att.event_date, groupby=db.sb_att.event_date)]
	return dates