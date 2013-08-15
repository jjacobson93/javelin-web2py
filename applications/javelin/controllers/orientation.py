# -*- coding: utf-8 -*-
"""
	Javelin Web2Py Orientation Controller
"""

from applications.javelin.modules import modules_enabled, get_module_data, orientation
from applications.javelin.private.utils import flattenDict, cached
from gluon.contrib import simplejson as json
from gluon.tools import Service
service = Service(globals())

@auth.requires_login()
@auth.requires_membership('standard')
def index():
	"""Loads the index page for the 'Orientation' controller

	:returns: a dictionary to pass to the view with the list of modules_enabled and the active module ('orientation')
	"""
	modules_data = get_module_data()
	existing_nametags = db().select(db.file.ALL)
	return dict(modules_enabled=modules_enabled, modules_data=modules_data, active_module='orientation', existing_nametags=existing_nametags)

@auth.requires_login()
@auth.requires_membership('standard')
@service.json
def attendance_data(event_id):
	return orientation.attendance_data(event_id)

@auth.requires_login()
@auth.requires_membership('standard')
@service.json
def quick_attendance(event_id, person_id=None, student_id=None, present=True):
	return orientation.quick_attendance(person_id, student_id, event_id, present)

@auth.requires_login()
@auth.requires_membership('standard')
@service.json
def make_labels(event_name, type, present=None, event_id=None):
	import time
	import os
	import StringIO
	from datetime import datetime

	year = datetime.now().year
	filename='labels'

	from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image, Spacer
	from reportlab.platypus.flowables import PageBreak
	from reportlab.lib.styles import ParagraphStyle
	from reportlab.lib.enums import TA_CENTER, TA_LEFT
	from reportlab.lib.pagesizes import letter, inch
	from reportlab.lib import colors

	doc_io = StringIO.StringIO()

	doc = SimpleDocTemplate(doc_io, pagesize=letter, 
		rightMargin=0.18*inch, leftMargin=0.18*inch, topMargin=0.4*inch, bottomMargin=0)

	elements = list()

	if type == 'leaders':
		people = db(db.person.leader==True).select(
			db.person.ALL, db.crew.room, db.crew.wefsk,
			left=db.crew.on(db.person.crew==db.crew.id),
			orderby=[db.person.last_name, db.person.first_name])

		if present is not None and event_id is not None:
			people = db(db.person.leader==True).select(
				db.person.ALL, db.crew.room, db.crew.wefsk,
				left=db.crew.on(db.person.crew==db.crew.id),
				join=db.attendance.on((db.person.id==db.attendance.person_id) & 
					(db.attendance.event_id==event_id) & 
					(db.attendance.present==present)),
				orderby=[db.person.last_name, db.person.first_name])

	else:
		people = db(db.person.grade==9).select(
			db.person.ALL, db.crew.room, db.crew.wefsk,
			left=db.crew.on(db.person.crew==db.crew.id),
			orderby=[db.person.last_name, db.person.first_name])

		if present is not None and event_id is not None:
			people = db(db.person.grade==9).select(
				db.person.ALL, db.crew.room, db.crew.wefsk,
				left=db.crew.on(db.person.crew==db.crew.id),
				join=db.attendance.on((db.person.id==db.attendance.person_id) & 
					(db.attendance.event_id==event_id) & 
					(db.attendance.present==present)),
				orderby=[db.person.last_name, db.person.first_name])

	centerStyle = ParagraphStyle(name='Center', alignment=TA_CENTER)
	leftStyle = ParagraphStyle(name='Left', alignment=TA_LEFT)
	tableStyle = TableStyle([('VALIGN',(0,-1),(-1,-1),'TOP')])
	label_num = 0
	row_num = 0
	labels = list()

	rotations = {
		'A' : {
			'I' : 'E1 -> P21 -> SS1 -> M1 -> P15',
			'II' : 'P21 -> SS1 -> M1 -> P15 -> E1',
			'III' : 'SS1 -> M1 -> P15 -> E1 -> P21',
			'IV' : 'M1 -> P15 -> E1 -> P21 -> SS1',
			'V' : 'P15 -> E1 -> P21 -> SS1 -> M1'
		},
		'B' : {
			'I' : 'E2 -> P23 -> SS3 -> M2 -> P16',
			'II' : 'P23 -> SS3 -> M2 -> P16 -> E2',
			'III' : 'SS3 -> M2 -> P16 -> E2 -> P23',
			'IV' : 'M2 -> P16 -> E2 -> P23 -> SS3',
			'V' : 'P16 -> E2 -> P23 -> SS3 -> M2'
		},
		'C' : {
			'I' : 'E3 -> P24 -> SS4 -> M3 -> P17',
			'II' : 'P24 -> SS4 -> M3 -> P17 -> E3',
			'III' : 'SS4 -> M3 -> P17 -> E3 -> P24',
			'IV' : 'M3 -> P17 -> E3 -> P24 -> SS4',
			'V' : 'P17 -> E3 -> P24 -> SS4 -> M3'
		},
		'D' : {
			'I' : 'E4 -> P25 -> SS5 -> M4 -> P18',
			'II' : 'P25 -> SS5 -> M4 -> P18 -> E4',
			'III' : 'SS5 -> M4 -> P18 -> E4 -> P25',
			'IV' : 'M4 -> P18 -> E4 -> P25 -> SS5',
			'V' : 'P18 -> E4 -> P25 -> SS5 -> M4'
		},
		'E' : {
			'I' : 'E5 -> P26 -> SS6 -> M5 -> P19',
			'II' : 'P26 -> SS6 -> M5 -> P19 -> E5',
			'III' : 'SS6 -> M5 -> P19 -> E5 -> P26',
			'IV' : 'M5 -> P19 -> E5 -> P26 -> SS6',
			'V' : 'P19 -> E5 -> P26 -> SS6 -> M5'
		}
	}

	def rotation(station, letter):
		return rotations[station][letter]

	for row in people:
		
		label = list()

		if label_num == 2:
			table = Table([labels], colWidths=[4*inch,0.14*inch,4*inch], rowHeights=[2*inch]*(len(labels)/2))
			table.setStyle(tableStyle)
			elements.append(table)

			label_num = 0
			labels = list()
			row_num += 1
			if row_num == 5:
				row_num = 0
				elements.append(PageBreak())

		header = Paragraph("<font face='Times-Bold' size=11>{} {}</font>".format(year, event_name), centerStyle)

		label.append(header)
		label.append(Spacer(1,11))

		firstName = Paragraph("<font face='Times-Bold' size=18>{}</font>".format(row.person.first_name), centerStyle)
		label.append(firstName)
		label.append(Spacer(1, 11))

		lastName = Paragraph("<font face='Times-Roman' size=11>{}</font>".format(row.person.last_name), centerStyle)
		label.append(lastName)
		label.append(Spacer(1,20))

		if row.crew.wefsk != '' or row.crew.wefsk != None or row.crew.wefsk != 'N/A':
			try:
				rooms = rotation(row.crew.wefsk.split('-')[0], row.crew.wefsk.split('-')[1])
			except:
				rooms = 'N/A'
		else:
			rooms = 'N/A'

		label.append(Paragraph("<font face='Times-Roman' size=11>ID#: {}</font>".format(row.person.student_id), leftStyle))
		label.append(Paragraph("<font face='Times-Roman' size=11>Crew #: {}</font>".format(row.person.crew), leftStyle))

		label.append(Paragraph("<font face='Times-Roman' size=11>Crew Room: {}</font>".format(row.crew.room), leftStyle))
		label.append(Paragraph("<font face='Times-Roman' size=11>W.E.F.S.K. Rotation: {}</font>".format(rooms), leftStyle))

		labels.append(label)

		if label_num == 0:
			labels.append(Spacer(14, 144))

		label_num += 1

	doc.build(elements)

	from pypdf2 import PdfFileWriter, PdfFileReader
	from reportlab.pdfgen.canvas import Canvas
	from reportlab.lib.pagesizes import letter

	doc_io.seek(0)
	existing = PdfFileReader(doc_io)
	imagefile = "{}/applications/javelin/static/images/vc2emblem.jpg".format(os.getcwd())

	packet = StringIO.StringIO()
	canvas = Canvas(packet, pagesize=letter)

	x_values = [36, 240, 334, 542]
	y = 708
	for i in range(20):
		x = x_values[i%4]
		if i%4 == 0 and i != 0:
			y -= 144
		canvas.drawImage(imagefile, x, y, 32, 32)

	canvas.showPage()
	canvas.save()

	packet.seek(0)
	emblems = PdfFileReader(packet)

	writer = PdfFileWriter()

	for page in existing.pages:
		page.mergePage(emblems.getPage(0))
		writer.addPage(page)

	output = StringIO.StringIO()
	writer.write(output)
	output.seek(0)


	filename = "{}_{}_{}.pdf".format('_'.join(event_name.lower().split()),filename, int(time.time()))

	file_id = db.file.insert(name=filename, file=db.file.file.store(output, filename))

	db_file = db.file(file_id).file

	return dict(filename=db_file)
	# return orientation.make_labels(event_name, type, filename)

@auth.requires_login()
@auth.requires_membership('standard')
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
			rows = [['Yes/No?', 'ID', 'Last Name', 'First Name', 'Cell Phone']] +\
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

		crews = db().select(db.crew.ALL, orderby=db.crew.id)
		for c in crews:
			freshmen = db((db.person.grade==9) & 
				(db.person.crew==c.id)).select(db.person.ALL, 
				orderby=[db.person.last_name, db.person.first_name])
			elements.append(Paragraph("<font face='Helvetica-Bold' size=16>Attendance " +\
				" - Crew: {}, Room: {}, WEFSK: {}</font>".format(
					c.id, c.room, c.wefsk), leftStyle))
			elements.append(Spacer(1, 16))
			rows = [['Yes/No?', 'ID', 'Sex', 'Last Name', 'First Name']] +\
				   [['', s.student_id, s.gender, s.last_name, s.first_name] for s in freshmen]
			table = Table(rows, colWidths=[(width - (rightleftMargin*2))*.1,
				(width - (rightleftMargin*2))*.1, (width - (rightleftMargin*2))*.1, 
				(width - (rightleftMargin*2))*.35, (width - (rightleftMargin*2))*.35], 
				rowHeights=[.5*inch]*(len(freshmen) + 1))
			table.setStyle(tableStyle)
			elements.append(table)
			elements.append(Spacer(1,16))
			elements.append(Paragraph("<font face='Helvetica-Oblique' size=12>Notes:</font>", leftStyle))
			elements.append(PageBreak())

	elif kind == 'call_homes':
		title = 'call_homes'
		crews = db().select(db.crew.ALL, orderby=db.crew.id)
		for c in crews:
			freshmen = db((db.person.grade==9) & 
				(db.person.crew==c.id)).select(db.person.ALL, 
				orderby=[db.person.last_name, db.person.first_name])
			elements.append(Paragraph("<font face='Helvetica-Bold' size=16>Call Home List - Crew: {}</font>".format(c.id), leftStyle))
			elements.append(Spacer(1, 16))

			elements.append(Paragraph("<font face='Helvetica' size=12><u>SCRIPT FOR CALLING YOUR FRESHMEN</u></font>", leftStyle));
			elements.append(Paragraph("1. Introduce yourself", leftStyle));
			elements.append(Paragraph("2. Tell them they're on your Crusher Crew team (which also happens to be the best!)", leftStyle));
			elements.append(Paragraph("3. Remind them that Orientation Day is tomorrow, Friday the 9th, and they should be at the gym by 7:55 am.", leftStyle));
			elements.append(Paragraph("4. Tell them to wear comfortable clothes as it will be a very active day. There is no need to bring a backpack.", leftStyle));
			elements.append(Paragraph("5. Tell them they need to bring the paperwork sent home over the summer (Pink and green Emergency forms, etc.)", leftStyle));
			elements.append(Paragraph("6. Tell them they will pick up their class schedules during the day.", leftStyle));
			elements.append(Paragraph("7. The day will be over around 3:00 or 3:15 and that they can pick up their textbooks between 3:00 and 4:00 in the library if they want to.", leftStyle));
			elements.append(Paragraph("8. Ask if they have any questions.", leftStyle));
			elements.append(Paragraph("9. Tell them you look forward to meeting them.", leftStyle));
			elements.append(Paragraph("10. Good bye!", leftStyle));
			elements.append(Spacer(1,16))

			rows = [['Last Name', 'First Name', 'Gender', 'Home Phone']] +\
				   [[s.last_name, s.first_name, s.gender, s.home_phone] for s in freshmen]
			table = Table(rows, colWidths=[(width - (rightleftMargin*2))*.35,
				(width - (rightleftMargin*2))*.35, (width - (rightleftMargin*2))*.1,
				(width - (rightleftMargin*2))*.2], 
				rowHeights=[.3*inch]*(len(freshmen) + 1))
			table.setStyle(tableStyle)
			elements.append(table)
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
@auth.requires_membership('standard')
@service.json
def crews(id=None):
	return orientation.crews(id)

@auth.requires_login()
@auth.requires_membership('standard')
@service.json
def crew_records(id):
	return orientation.crew_records(id)

@auth.requires_login()
@auth.requires_membership('standard')
@service.json
def add_crew(room, wefsk, people):
	return orientation.add_crew(room, wefsk, json.loads(people))

@auth.requires_login()
@auth.requires_membership('standard')
@service.json
def people_not_in_crew(id, query):
	return orientation.people_not_in_crew(id, query)

@auth.requires_login()
@auth.requires_membership('standard')
@service.json
def add_people_to_crew(id, people):
	return orientation.add_people_to_crew(id, json.loads(people))

@auth.requires_login()
@auth.requires_membership('standard')
@service.json
def remove_crew(person_id):
	return orientation.remove_crew(person_id)

@auth.requires_login()
@auth.requires_membership('standard')
@service.json
def move_to_crew(id, person_id):
	return orientation.move_to_crew(id, person_id)

@auth.requires_login()
@auth.requires_membership('standard')
@service.json
def update_room(id, room, wefsk):
	return orientation.update_room(id, room, wefsk)

@auth.requires_login()
@auth.requires_membership('standard')
@service.json
def organize_crews():
	return orientation.organize_crews()

@auth.requires_login()
@auth.requires_membership('standard')
def call():
	"""Call function used when calling a function from an HTTP request"""
	return service()