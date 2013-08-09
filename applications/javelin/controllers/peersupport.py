# -*- coding: utf-8 -*-
"""
	Javelin Web2Py Peer Support Controller
"""

from gluon.tools import Service
from gluon.sqlhtml import FormWidget
service = Service(globals())

@auth.requires_login()
@auth.requires(auth.has_membership('peer_support') or auth.has_membership('admin')) 
def index():
	student = db.person.with_alias('student')
	peer_support = db.person.with_alias('peer_support')
	issues = db().select(db.student_issue.ALL, student.ALL, peer_support.ALL, db.crew.ALL,
		join=[student.on(student.id==db.student_issue.person_id),
			peer_support.on(peer_support.id==db.student_issue.ps_id)],
		left=db.crew.on(db.student.crew==db.crew.id))

	return dict(issues=issues)

@auth.requires_login()
@auth.requires(auth.has_membership('peer_support') or auth.has_membership('admin'))
def new_issue():
	form = SQLFORM(db.student_issue,
		fields=['person_id', 'ps_id', 'summary', 'result', 'need_follow_up', 'refer'],
		formstyle='table2cols')
	if form.process(next=URL(a='javelin', c='peersupport', f='index')).accepted:
		response.flash = 'The issue has been submitted!'
	elif form.errors:
		response.flash = 'There are errors in the form'
	return dict(form=form)

@auth.requires_login()
@auth.requires(auth.has_membership('peer_support') or auth.has_membership('admin'))
def issue():
	id = int(request.vars.id[-1])
	student = db.person.with_alias('student')
	peer_support = db.person.with_alias('peer_support')
	if id:
		issue = db(db.student_issue.id==id).select(db.student_issue.ALL, student.ALL, peer_support.ALL, db.crew.ALL,
			join=[student.on(student.id==db.student_issue.person_id),
				peer_support.on(peer_support.id==db.student_issue.ps_id)],
			left=db.crew.on(db.student.crew==db.crew.id)).first()
		if issue:
			return dict(issue=issue)

	return dict(issue=None)

@auth.requires_login()
@auth.requires(auth.has_membership('peer_support') or auth.has_membership('admin'))
def follow_up():
	id = int(request.vars.id[-1])
	db.student_issue.id.readable = False

	db.student_issue.person_id.writable = False
	# db.student_issue.person_id.represent = lambda row: ' '.join([row.first_name, row.last_name])

	db.student_issue.ps_id.writable = False
	# db.student_issue.ps_id.represent = lambda row: ' '.join([row.first_name, row.last_name])

	db.student_issue.result.writable = False
	db.student_issue.summary.writable = False

	db.student_issue.result.label = 'Result of Campus Walk'

	form = SQLFORM(db.student_issue, id,
		fields=['person_id', 'ps_id', 'summary', 'result', 'follow_up'],
		formstyle='table2cols')
	if form.process(next=URL(a='javelin', c='peersupport', f='index')).accepted:
		db(db.student_issue.id==id).update(need_follow_up=False)
		response.flash = 'The issue has been submitted!'
	elif form.errors:
		response.flash = 'There are errors in the form'
	return dict(form=form)

def form_row(record_id, field_label, field_widget, field_comment):
	return TR()
