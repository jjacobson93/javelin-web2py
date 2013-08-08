# -*- coding: utf-8 -*-
"""
	Javelin Web2Py Orientation Controller
"""

from applications.javelin.modules import modules_enabled, get_module_data, orientation
from gluon.contrib import simplejson as json
from gluon.tools import Service
service = Service(globals())

@auth.requires_login()
def index():
	"""Loads the index page for the 'Orientation' controller

	:returns: a dictionary to pass to the view with the list of modules_enabled and the active module ('orientation')
	"""
	modules_data = get_module_data()
	existing_nametags = db().select(db.file.ALL)
	return dict(modules_enabled=modules_enabled, modules_data=modules_data, active_module='orientation', existing_nametags=existing_nametags)

@auth.requires_login()
@service.json
def attendance_data(event_id):
	return orientation.attendance_data(event_id)

@auth.requires_login()
@service.json
def quick_attendance(event_id, person_id=None, student_id=None, present=True):
	return orientation.quick_attendance(person_id, student_id, event_id, present)

@auth.requires_login()
@service.json
def make_labels(event_name, type, filename='labels'):
	return orientation.make_labels(event_name, type, filename)

@auth.requires_login()
@service.json
def attendance_sheet(kind):
	import StringIO
	import time
	import cgi

	from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image, Spacer
	from reportlab.platypus.flowables import PageBreak
	from reportlab.lib.styles import ParagraphStyle
	from reportlab.lib.enums import TA_CENTER, TA_LEFT
	from reportlab.lib.pagesizes import letter, inch
	from reportlab.lib import colors

	io = StringIO.StringIO()
	rightleftMargin = 45
	topbottomMargin = 73 
	width, height = letter

	doc = SimpleDocTemplate(io, pagesize=letter,
			rightMargin=rightleftMargin, 
			leftMargin=rightleftMargin, 
			topMargin=topbottomMargin, 
			bottomMargin=topbottomMargin)

	elements = list()

	centerStyle = ParagraphStyle(name='Center', alignment=TA_CENTER)
	leftStyle = ParagraphStyle(name='Left', alignment=TA_LEFT)
	tableStyle = TableStyle([
		('VALIGN',(0,0),(-1,-1),'MIDDLE'),
		('GRID', (0,0), (-1,-1), 1, colors.black),
		('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
		('FONT', (0, 1), (-1, -1), 'Helvetica')])

	if kind == 'task_teams': # Task Teams
		title = 'task_team_attendance'
	
		teams = db().select(db.groups.ALL)
		for t in teams:
			students = db().select(db.person.ALL, join=db.person.on(db.person.id==db.group_rec.person_id))

			elements.append(Paragraph("<font face='Helvetica-Bold' size=16>{}</font>".format(cgi.escape(t.name)), leftStyle))
			elements.append(Spacer(1, 16))
			rows = [['Present?', 'ID', 'Last Name', 'First Name', 'Cell Phone']] +\
				   [['', s.student_id, s.last_name, s.first_name, s.cell_phone] for s in students]
			table = Table(rows, colWidths=[(width - (rightleftMargin*2))*.1,
				(width - (rightleftMargin*2))*.1, (width - (rightleftMargin*2))*.30, 
				(width - (rightleftMargin*2))*.30, (width - (rightleftMargin*2))*.2], 
				rowHeights=[.5*inch]*(len(students) + 1))
			table.setStyle(tableStyle)
			elements.append(table)
			elements.append(Spacer(1, 16))
			elements.append(Paragraph("<font face='Helvetica-Oblique' size=12>Notes:</font>", leftStyle))
			elements.append(PageBreak())

	elif kind == 'crew_freshmen':
		title = 'crew_freshmen_attendance'

		crews = db().select(db.crew.ALL)
		for c in crews:
			freshmen = db((db.person.grade==9) & (db.person.crew==c.id)).select(db.person.ALL)
			elements.append(Paragraph("<font face='Helvetica-Bold' size=16>Attendance " +\
				" - Crew: {}, Room: {}, WEFSK: {}</font>".format(
					c.id, c.room, c.wefsk), leftStyle))
			elements.append(Spacer(1, 16))
			rows = [['Present?', 'ID', 'Sex', 'Last Name', 'First Name']] +\
				   [['', s.student_id, s.gender, s.last_name, s.first_name] for s in students]
			table = Table(rows, colWidths=[(width - (rightleftMargin*2))*.1,
				(width - (rightleftMargin*2))*.1, (width - (rightleftMargin*2))*.1, 
				(width - (rightleftMargin*2))*.35, (width - (rightleftMargin*2))*.35], 
				rowHeights=[.5*inch]*(len(students) + 1))
			table.setStyle(tableStyle)
			elements.append(table)
			elements.append(Spacer(1,16))
			elements.append(Paragraph("<font face='Helvetica-Oblique' size=12>Notes:</font>", leftStyle))
			elements.append(PageBreak())

	if kind and elements:
		doc.build(elements)

		io.seek(0)

		filename = "{}_{}.pdf".format(title, int(time.time()))

		file_id = db.file.insert(name=filename, file=db.file.file.store(io, filename))

		db_file = db.file(file_id).file

		return dict(filename=db_file)

	return dict(error=True)

@auth.requires_login()
@service.json
def crews(id=None):
	return orientation.crews(id)

@auth.requires_login()
@service.json
def crew_records(id):
	return orientation.crew_records(id)

@auth.requires_login()
@service.json
def add_crew(room, wefsk, people):
	return orientation.add_crew(room, wefsk, json.loads(people))

@auth.requires_login()
@service.json
def people_not_in_crew(id, query):
	return orientation.people_not_in_crew(id, query)

@auth.requires_login()
@service.json
def add_people_to_crew(id, people):
	return orientation.add_people_to_crew(id, json.loads(people))

@auth.requires_login()
@service.json
def remove_crew(person_id):
	return orientation.remove_crew(person_id)

@auth.requires_login()
@service.json
def move_to_crew(id, person_id):
	return orientation.move_to_crew(id, person_id)

@auth.requires_login()
@service.json
def update_room(id, room, wefsk):
	return orientation.update_room(id, room, wefsk)

@auth.requires_login()
@service.json
def organize_crews():
	return orientation.organize_crews()

@auth.requires_login()
def call():
	"""Call function used when calling a function from an HTTP request"""
	return service()