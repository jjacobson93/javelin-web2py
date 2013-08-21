# -*- coding: utf-8 -*-
"""
	Javelin SB Web2Py Grades Controller
"""

from gluon.storage import Storage

@auth.requires_login()
def index():
	people = db(db.person.id>0).select(db.person.id, 
		db.person.last_name, db.person.first_name,
		orderby=db.person.last_name|db.person.first_name)

	sessions = db(db.grade_session.id>0).select()

	# result = [Storage(last_name=p.last_name, first_name=p.first_name,
	# 			grades=dict([(g.grade_session.title, GRADES[g.grade.grade]) for g in grades_for(p.id)])) for p in people]

	return dict(people=people, sessions=sessions)


@auth.requires_login()
def table():
	person_id = request.vars.get('person_id', None)

	sessions = db(db.grade_session.id>0).select(orderby=db.grade_session.date)

	if person_id:
		data = db(db.person.id==person_id).select(db.person.id, db.person.last_name, db.person.first_name,
				db.course.title, db.teacher.teacher_name, db.course_rec.id,
				join=[db.course_rec.on(db.person.id==db.course_rec.student_id),
					db.course.on(db.course.id==db.course_rec.course_id),
					db.teacher.on(db.teacher.id==db.course.teacher_id)])
					# db.grade.on(db.course_rec.id==db.grade.course_rec_id),
					# db.grade_session.on((db.grade_session.id==db.grade.session_id))])


		result = [Storage(course_title=d.course.title, teacher_name=d.teacher.teacher_name,
			sessions=[db(db.person.id==person_id).select(db.person.id, db.grade.ALL, db.grade_session.ALL,
				join=[db.course_rec.on((db.person.id==db.course_rec.student_id) & (db.course_rec.id==d.course_rec.id)),
					db.grade.on(db.course_rec.id==db.grade.course_rec_id),
					db.grade_session.on((db.grade_session.id==db.grade.session_id) & (db.grade_session.id==s.id))]).first() for s in sessions]) for d in data]
		return dict(data=result, sessions=sessions)
	else:
		return dict(data=None, sessions=sessions)

