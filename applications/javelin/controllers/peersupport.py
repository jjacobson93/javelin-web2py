# -*- coding: utf-8 -*-
"""
	Javelin Web2Py Peer Support Controller
"""

# metadata
__author__ = "Jeremy Jacobson"
__copyright__ = "(c) 2013, Jacobson and Varni, LLC"
__date__ = "7/12/2013"
__email__ = "jjacobson93@gmail.com"
__data__ = {'name' : 'peersupport', 'label' : 'Peer Support', 'description' : 'Issue tracking system for Peer Support', 
	'icon' : 'heart', 'u-icon' : u'\uf004', 'color': 'pink', 'required' : True}

from applications.javelin.ctr_data import ctr_enabled, get_ctr_data
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

	reports = db(db.file.name.contains("Peer_Support")).select(db.file.ALL)


	return dict(issues=issues, reports=reports, ctr_enabled=ctr_enabled, ctr_data=get_ctr_data(), active_module='peersupport')

@auth.requires_login()
@auth.requires(auth.has_membership('peer_support') or auth.has_membership('admin'))
def new_issue():
	form = SQLFORM(db.student_issue,
		fields=['person_id', 'ps_id', 'summary', 'result', 'need_follow_up', 'refer'],
		formstyle='divs')
	if form.process(next=URL(a='javelin', c='peersupport', f='index')).accepted:
		response.flash = 'The issue has been submitted!'
	elif form.errors:
		response.flash = 'There are errors in the form'

	return dict(form=form, ctr_enabled=ctr_enabled, active_module='peersupport', ctr_data=get_ctr_data())

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
			return dict(issue=issue, ctr_enabled=ctr_enabled, active_module='peersupport', ctr_data=get_ctr_data())

	return dict(issue=None, ctr_enabled=ctr_enabled, active_module='peersupport', ctr_data=get_ctr_data())

@auth.requires_login()
@auth.requires(auth.has_membership('peer_support') or auth.has_membership('admin'))
def follow_up():
	id = int(request.vars.id[-1])
	db.student_issue.id.readable = False

	db.student_issue.person_id.writable = False
	db.student_issue.person_id.represent = lambda row: ' '.join([row.first_name, row.last_name])

	db.student_issue.ps_id.writable = False
	db.student_issue.ps_id.represent = lambda row: ' '.join([row.first_name, row.last_name])

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
	return dict(form=form, ctr_enabled=ctr_enabled, active_module='peersupport', ctr_data=get_ctr_data())

@auth.requires_login()
@auth.requires(auth.has_membership('peer_support') or auth.has_membership('admin'))
@service.json
def generate_report():
	import StringIO
	from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image, Spacer
	from reportlab.platypus.flowables import PageBreak
	from reportlab.lib.styles import ParagraphStyle
	from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
	from reportlab.lib.pagesizes import letter, inch
	from reportlab.lib import colors

	try:
		id = int(request.vars.id[-1])
	except:
		id = -1

	io = StringIO.StringIO()

	doc = SimpleDocTemplate(io, pagesize=letter, 
		rightMargin=0.25*inch, leftMargin=0.25*inch, topMargin=0.25*inch, bottomMargin=0)

	elements = list()

	centerStyle = ParagraphStyle(name='Center', alignment=TA_CENTER)
	leftStyle = ParagraphStyle(name='Left', alignment=TA_LEFT)
	rightStyle = ParagraphStyle(name='Right', alignment=TA_RIGHT)
	tableStyle = TableStyle([
		('VALIGN',(0,0),(-1,-1),'MIDDLE'),
		('VALIGN',(1,8),(1,-1),'TOP'),
		('GRID', (0,0), (-1,-1), 1, colors.black),
		('FONT', (0, 0), (0, -1), 'Helvetica-Bold')])

	if id != -1:
		student = db.person.with_alias('student')
		peer_support = db.person.with_alias('peer_support')
		issue = db(db.student_issue.id==id).select(db.student_issue.ALL, student.ALL, peer_support.ALL, db.crew.ALL,
			join=[student.on(student.id==db.student_issue.person_id),
				peer_support.on(peer_support.id==db.student_issue.ps_id)],
			left=db.crew.on(db.student.crew==db.crew.id)).first()

		output = StringIO.StringIO()

		l = list()
		for field in issue:
			l.append(field)

	else:
		student = db.person.with_alias('student')
		peer_support = db.person.with_alias('peer_support')
		issues = db().select(db.student_issue.ALL, student.ALL, peer_support.ALL, db.crew.ALL,
			join=[student.on(student.id==db.student_issue.person_id),
				peer_support.on(peer_support.id==db.student_issue.ps_id)],
			left=db.crew.on(db.student.crew==db.crew.id))


		numpage = len(issues)
		p = 1

		import calendar
		from datetime import datetime, timedelta

		def utc_to_local(utc_dt):
			# get integer timestamp to avoid precision lost
			timestamp = calendar.timegm(utc_dt.timetuple())
			local_dt = datetime.fromtimestamp(timestamp)
			assert utc_dt.resolution >= timedelta(microseconds=1)
			return local_dt.replace(microsecond=utc_dt.microsecond)

		for i in issues:
			elements.append(Paragraph("<font face='Helvetica' size=11>Page {} of {}</font>".format(p, numpage), rightStyle))
			elements.append(Paragraph("<font face='Helvetica-Bold' size=16>Peer Support Issue #{}</font>".format(i.student_issue.id), leftStyle))
			elements.append(Spacer(1, 16))

			rows = [['Date/Time', utc_to_local(i.student_issue.timestamp)],
				['Student ID#', Paragraph("{}".format(i.student.student_id), leftStyle)],
				['Last Name', Paragraph("{}".format(i.student.last_name), leftStyle)],
				['First Name', Paragraph("{}".format(i.student.first_name), leftStyle)],
				['Grade', Paragraph("{}".format(i.student.grade), leftStyle)],
				['Peer Support Student', Paragraph("{}".format(i.peer_support.last_name + ', ' + i.peer_support.first_name), leftStyle)],
				['Need Follow Up?', Paragraph("{}".format('Yes' if i.student_issue.need_follow_up else 'No'), leftStyle)],
				['Refer to PS?', Paragraph("{}".format('Yes' if i.student_issue.refer else 'No'), leftStyle)],
				['Summary of Concert', Paragraph("{}".format(i.student_issue.summary), leftStyle)],
				['Result of Campus Walk', Paragraph("{}".format(i.student_issue.result), leftStyle)],
				['Follow Up Notes', Paragraph("{}".format(i.student_issue.follow_up), leftStyle)]]

			table = Table(rows, colWidths=[1.75*inch, 6.25*inch], 
				rowHeights=[.5*inch, .5*inch, .5*inch, .5*inch,
					.5*inch, .5*inch, .5*inch, .5*inch,
					1.8*inch, 1.8*inch, 1.8*inch])
			table.setStyle(tableStyle)
			elements.append(table)

			elements.append(Spacer(1, 16))
			elements.append(Paragraph("<font face='Helvetica' size=10>Created On: {}</font>".format(datetime.now().strftime('%Y-%m-%d')), rightStyle))
			elements.append(PageBreak())

			p += 1

	doc.build(elements)
	io.seek(0)

	import time
	now = datetime.now().strftime('%Y-%m-%d')

	filename = "{}_{}_{}.pdf".format('Peer_Support_Report', now, int(time.time()))

	file_id = db.file.insert(name=filename, file=db.file.file.store(io, filename))

	db_file = db.file(file_id).file

	return dict(filename=db_file)

@auth.requires_login()
@auth.requires(auth.has_membership('peer_support') or auth.has_membership('admin'))
def call():
	"""Call function used when calling a function from an HTTP request"""
	return service()
