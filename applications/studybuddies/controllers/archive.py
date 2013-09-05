# -*- coding: utf-8 -*-
"""
	Javelin SB Web2Py Archive Controller
"""

from gluon.storage import Storage

@auth.requires_login()
def index():
	currdate = request.now.strftime('%Y-%m-%d-%H-%M-%S') #this is UTC time
	return dict(currdate=currdate)

@auth.requires_login()
def table():
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
				orderby=db.person.last_name|db.person.first_name)

		students = list()
		for p in records:
			s = Storage(subjects=[],sb_att_ids=[], sb_void=[], in_time=None, out_time=None, **dict((c,v) for c, v in p.items()))
			for r in recordsfor(p.person.id):
				s.subjects.append(str(r.sb_section.title))
				s.sb_att_ids.append(int(r.sb_att.id))
				s.sb_void.append(r.sb_att.void)
				if not s.in_time or (r.sb_att.in_time and r.sb_att.in_time < s.in_time):
					s.in_time = r.sb_att.in_time

				if not s.out_time or (r.sb_att.out_time and r.sb_att.out_time > s.out_time):
					s.out_time = r.sb_att.out_time

			s.subjects = ', '.join(s.subjects)
			s.totaltime = s.out_time - s.in_time

			students.append(s)

		students = sorted(students, key=lambda s: s.person.last_name)

		return dict(students=students)

	return dict(students=list())