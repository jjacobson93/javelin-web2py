# -*- coding: utf-8 -*-
"""
	Javelin SB Web2Py Tutors Controller
"""

from gluon.storage import Storage

@auth.requires_login()
def index():
	group = db(((db.groups.name.like('%tutor%')) | (db.groups.name.like('%tutor%')))).select(db.groups.id).first()

	if group:
		tutors = db().select(db.person.student_id, db.person.last_name, db.person.first_name, db.person.grade, db.study_buddy.ALL,
			join=[db.group_rec.on(db.person.id==db.group_rec.person_id),
				db.groups.on((db.groups.id==db.group_rec.group_id) & (db.groups.id==group.id)),
				db.study_buddy.on(db.person.id==db.study_buddy.person_id)])
	else:
		tutors = None

	return dict(tutors=tutors)