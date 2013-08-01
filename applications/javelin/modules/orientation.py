# -*- coding: utf-8 -*-
"""
	Javelin Web2Py Orientation Module
"""

# metadata
__author__ = "Jeremy Jacobson"
__copyright__ = "(c) 2013, Jacobson and Varni, LLC"
__date__ = "7/16/2013"
__email__ = "jjacobson93@gmail.com"
__data__ = {'name' : 'orientation', 'label' : 'Orientation', 'description' : 'The interface for Crusher Crew Orientation', 
	'icon' : 'compass', 'u-icon' : u'\uf14e', 'required' : True}

from globals import current
from applications.javelin.private.utils import flattenDict

def attendance_data(event_id):
	db = current.javelin.db

	# data = db((db.attendance.event_id==event_id) | (db.attendance.event_id==None)).select(db.person.id, 
	# 	db.person.last_name, db.person.first_name,
	# 	db.attendance.present, db.attendance.event_id, db.events.title,
	# 	left=[db.attendance.on(db.person.id==db.attendance.person_id),
	# 	db.events.on(db.events.id==db.attendance.event_id)],
	# 	orderby=db.person.id).as_list()

	data = db((db.person.grade==9) | (db.person.leader==True)).select(db.person.id, db.person.last_name, db.person.first_name,
		db.attendance.present, db.attendance.event_id, db.events.title, db.person.grade,
		left=[db.attendance.on((db.person.id==db.attendance.person_id) & (db.attendance.event_id==event_id)),
		db.events.on(db.events.id==db.attendance.event_id)],
		orderby=db.person.id).as_list()

	data = [dict(('_'.join(k),v) if k != ('person','id') else ('id',v) for k,v in flattenDict(d).items()) for d in data]

	return data

def quick_attendance(person_id, event_id, present):
	db = current.javelin.db

	response = db.attendance.update_or_insert((db.attendance.person_id==person_id) & (db.attendance.event_id==event_id),
		person_id=person_id, event_id=event_id, present=present)

	return dict(response=response)

def make_labels(event_name, type, filename='labels'):
	db = current.javelin.db

	import time
	import os
	import StringIO
	from datetime import datetime

	year = datetime.now().year

	from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image, Spacer
	from reportlab.platypus.flowables import PageBreak
	from reportlab.lib.styles import ParagraphStyle
	from reportlab.lib.enums import TA_CENTER, TA_LEFT
	from reportlab.lib.pagesizes import letter, inch
	from reportlab.lib import colors

	doc_io = StringIO.StringIO()

	doc = SimpleDocTemplate(doc_io, pagesize=letter, 
		rightMargin=0.16*inch, leftMargin=0.16*inch, topMargin=0.5*inch, bottomMargin=0)

	elements = list()

	people = db().select(db.person.ALL).as_list()

	centerStyle = ParagraphStyle(name='Center', alignment=TA_CENTER)
	leftStyle = ParagraphStyle(name='Left', alignment=TA_LEFT)
	tableStyle = TableStyle([('VALIGN',(0,-1),(-1,-1),'TOP')])
	label_num = 0
	row_num = 0
	labels = list()
	for person in people:
		
		label = list()

		if label_num == 2:
			table = Table([labels], colWidths=[4*inch,0.19*inch,4*inch], rowHeights=[2*inch])
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

		firstName = Paragraph("<font face='Times-Bold' size=18>{}</font>".format(person['first_name']), centerStyle)
		label.append(firstName)
		label.append(Spacer(1, 11))

		lastName = Paragraph("<font face='Times-Roman' size=11>{}</font>".format(person['last_name']), centerStyle)
		label.append(lastName)
		label.append(Spacer(1,20))

		label.append(Paragraph("<font face='Times-Roman' size=11>ID#: {}</font>".format(person['id']), leftStyle))
		label.append(Paragraph("<font face='Times-Roman' size=11>Crew #: {}</font>".format(0), leftStyle))
		label.append(Paragraph("<font face='Times-Roman' size=11>Crew Room: {}</font>".format('N/A'), leftStyle))
		label.append(Paragraph("<font face='Times-Roman' size=11>W.E.F.S.K. Rotation: {}</font>".format('N/A'), leftStyle))

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

def crews():
	db = current.javelin.db

	crews = db().select(db.crew.ALL).as_list()

	return crews

def crew_records(id):
	db = current.javelin.db

	crew = db(db.person.crew==id).select(db.person.ALL).as_list()

	return crew

def add_crew(room, wefsk, people):
	db = current.javelin.db

	id = db.crew.insert(room=room, wefsk=wefsk)
	for p in people:
		db(db.person.id==p).update(crew=id)

	return dict(id=id)

def add_people_to_crew(id, people):
	db = current.javelin.db

	response = list()

	for p_id in people:
		response.append(db(db.person.id==p_id).update(crew=id))

	return dict(response=response)

def people_not_in_crew(id, query):
	db = current.javelin.db
	if id != 0:
		return db(((db.person.crew != id) | (db.person.crew == None)) & 
			((db.person.leader==True) | (db.person.grade==9)) & 
				((db.person.last_name.contains(query)) |
				 (db.person.first_name.contains(query)))).select(
			db.person.id, db.person.last_name, db.person.first_name).as_list()
	else:
		return db((db.person.crew == None) & 
			(((db.person.leader==True) | (db.person.grade==9)) & 
				((db.person.last_name.contains(query)) | 
					(db.person.first_name.contains(query))))).select(
			db.person.id, db.person.last_name, db.person.first_name).as_list()