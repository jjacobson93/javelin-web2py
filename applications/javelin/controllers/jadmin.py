# -*- coding: utf-8 -*-
"""
	Javelin Web2Py Admin Controller
"""

import time
from datetime import datetime
from applications.javelin.modules import modules_enabled, admin
from gluon.contrib import simplejson as json
from gluon.tools import Service
from gluon.storage import Storage
service = Service(globals())

DOC_TYPES = Storage(
	CALLSLIP=Storage(value=0, label="Call Slip"),
	ATTSHEETS=Storage(value=1, label="Attendance Sheets"),
	NAMETAGS=Storage(value=2, label="Nametags")
)

@auth.requires_login()
@auth.requires_membership('admin')
def index():
	"""Loads the index page for the 'Admin' controller

	:returns: a dictionary to pass to the view with the list of modules_enabled and the active module ('admin')
	"""
	from applications.javelin.modules import get_module_data
	modules_data = get_module_data()
	users = db().select(db.auth_user.ALL)
	approvals = db(db.auth_user.registration_key=='pending').select(db.auth_user.ALL)
	return dict(modules_enabled=modules_enabled, modules_data=modules_data, active_module='jadmin', users=users, approvals=approvals, doctypes=DOC_TYPES)

@auth.requires_login()
@auth.requires_membership('admin')
@service.json
def create_doc(doctype, data):

	logger.debug("CREATE DOC CALLED")

	import StringIO

	from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image, Spacer
	from reportlab.platypus.flowables import PageBreak
	from reportlab.lib.styles import ParagraphStyle
	from reportlab.lib.enums import TA_CENTER, TA_LEFT
	from reportlab.lib.pagesizes import letter, inch
	from reportlab.lib import colors

	io = StringIO.StringIO()

	doc = SimpleDocTemplate(io, pagesize=letter, 
		rightMargin=0.18*inch, leftMargin=0.18*inch, topMargin=0.18*inch, bottomMargin=0)

	elements = list()

	doctype = int(doctype)

	if data: data = json.loads(data)

	if doctype == DOC_TYPES.CALLSLIP.value:
		doc_title = "Call_Slips"

		people = data['people']
		message = data['message']

		persons = list()

		for p in people:
			if p.startswith('group_'):
				group = db(db.group_rec.group_id==p.replace('group_', '')).select(db.person.id,
					join=db.group_rec.on(db.person.id==db.group_rec.person_id))
				for g in group:
					if g.id not in persons:
						persons.append(g.id)
			elif p.startswith('grade_'):
				grade = db(db.person.grade==p.replace('grade_', '')).select(db.person.id)
				for g in grade:
					if g.id not in persons:
						persons.append(g.id)
			elif p == 'all_leaders':
				leaders = db(db.person.leader==True).select(db.person.id)
				for l in leaders:
					if l.id not in persons:
						persons.append(l.id)
			elif p == 'all_people':
				allpeople = db().select(db.person.id)
				for a in allpeople:
					if a.id not in persons:
						persons.append(a.id)
			else:
				if p not in persons:
					persons.append(p)

		people = [Storage(id=pid, last_name=db(db.person.id==pid).select(db.person.last_name).first().last_name,
						first_name=db(db.person.id==pid).select(db.person.first_name).first().first_name,
						courses=['{}: {}'.format(c.period, c.room) for c in db().select(db.course.period, db.course.room,
						left=db.course_rec.on((db.course.id==db.course_rec.course_id) & (db.course_rec.student_id==pid)))]
					) for pid in persons]

		i = 0
		centerStyle = ParagraphStyle(name='Center', alignment=TA_CENTER)
		leftStyle = ParagraphStyle(name='Left', alignment=TA_LEFT)
		tableStyle = TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),
								('INNERGRID', (0,0), (-1,-1), 0.25, colors.black)])
		page = list()

		for person in people:
			page.append([Paragraph("<para alignment='left'><br></para>" +\
					   "<para alignment='center'><font face='Times-Bold' size=16>Vintage Crusher Crew</font><br><br><br></para>" +\
					   "<para alignment='left'><font face='Times' size=14><b>Name:</b> {} {}</font><br><br></para>".format(person.first_name, person.last_name) +\
					   "<para alignment='left'><font face='Times' size=12><b>Rooms:</b> {}</font><br><br></para>".format(', '.join(person.courses)) +\
					   "<para alignment='left'><font face='Times' size=12><b>Message:</b></font><br></para>" +\
					   "<para alignment='left'><font face='Times' size=12>{}</font></para>".format(message), leftStyle)])

			i = (i+1)%4
			if i == 0:
				table = Table(page, colWidths=[8*inch], rowHeights=[2.5*inch]*len(page))
				table.setStyle(tableStyle)
				elements.append(table)
				elements.append(PageBreak())
				page = list()

	elif doctype == DOC_TYPES.ATTSHEETS.value:
		pass

	elif doctype == DOC_TYPES.NAMETAGS.value:
		people = data['people']
		event_name = data['event_name']
		events = data['events']
		present = data['present']

		if present is not None and event_id is not None:
			if present == True:
				people = db((db.person.leader==True) & (db.attendance.present==True)).select(
					db.person.ALL, db.crew.room, db.crew.wefsk,
					left=[db.crew.on(db.person.crew==db.crew.id),
						db.attendance.on((db.person.id==db.attendance.person_id) & 
							(db.attendance.event_id==event_id))],
					orderby=[db.person.last_name, db.person.first_name])
			else:
				people = db((db.person.leader==True) & 
						((db.attendance.present==False) | (db.attendance.present==None))).select(
					db.person.ALL, db.crew.room, db.crew.wefsk,
					left=[db.crew.on(db.person.crew==db.crew.id),
						db.attendance.on((db.person.id==db.attendance.person_id) & 
							(db.attendance.event_id==event_id))],
					orderby=[db.person.last_name, db.person.first_name])
		else:
			people = db(db.person.leader==True).select(
				db.person.ALL, db.crew.room, db.crew.wefsk,
				left=db.crew.on(db.person.crew==db.crew.id),
				orderby=[db.person.last_name, db.person.first_name])

	doc.build(elements)
	io.seek(0)

	now = datetime.now().strftime('%Y-%m-%d')

	filename = "{}_{}_{}.pdf".format(doc_title, now, int(time.time()))

	file_id = db.file.insert(name=filename, file=db.file.file.store(io, filename))

	db_file = db.file(file_id).file

	return dict(filename=db_file)

@auth.requires_login()
@auth.requires_membership('admin')
@service.json
def update_names(names):
	response = admin.update_names(json.loads(names))
	errors = list()
	for i in range(len(response)):
		if response[i] == 0:
			errors.append(names[i])

	return dict(errors=errors)

@auth.requires_login()
@auth.requires_membership('admin')
@service.json
def approve_user(id):
	response = db(db.auth_user.id==id).update(registration_key='')
	return dict(response=response)

@auth.requires_login()
@auth.requires_membership('admin')
@service.json
def disapprove_user(id):
	response = db(db.auth_user.id==id).delete()
	return dict(response=response)

@auth.requires_login()
@auth.requires_membership('admin')
@service.json
def import_from_csv(csv_file):
	"""Imports records into the database from a CSV file

	:param file: the file to be imported
	:param contains_ids: a boolean value which specifies if the records have ids; default is True
	:returns: a dictionary with a response, either a 0 or 1, depending on success
	"""
	return admin.import_from_csv(csv_file, True)

@auth.requires_login()
@auth.requires_membership('admin')
@service.json
def import_from_query(csv_file, leaders):
	"""Imports records into the database from a CSV file (in the form of the queries from VHS)

	:param file: the file to be imported
	:returns: a dictionary with a response, either a 0 or 1, depending on success
	"""
	return admin.import_from_query(csv_file, True if leaders=="true" else False)

@auth.requires_login()
@auth.requires_membership('admin')
@service.json
def get_person_group_data(query=None):
	if query:
		qlist = query.split()
		query = query.lower()

		students = db(((db.person.last_name.contains(qlist, all=True)) | 
					(db.person.first_name.contains(qlist, all=True))) ).select(
				db.person.id, db.person.last_name, db.person.first_name, 
				orderby=db.person.last_name|db.person.first_name).as_list()

		allfields = [{'text': 'All', 'children':[d for d in [{'id':'all_people', 'last_name':'All Students', 'first_name' : ''},
												{'id':'all_leaders', 'last_name':'All Leaders', 'first_name' : ''}] if query in d['last_name'].lower()]}]

		allfields = [] if not allfields[0]['children'] else allfields

		gradefields = [{'text': 'By Grade', 'children':[d for d in [{'id':'grade_9', 'last_name': 'Freshmen', 'first_name': ''},
													   {'id':'grade_10', 'last_name': 'Sophomores', 'first_name': ''},
													   {'id':'grade_11', 'last_name': 'Juniors', 'first_name': ''},
													   {'id':'grade_12', 'last_name': 'Seniors', 'first_name': ''}] if query in d['last_name'].lower()]}]

		gradefields = [] if not gradefields[0]['children'] else gradefields

		taskteams = [{'text': 'Task Teams', 'children': [{'id':'group_' + str(g.id), 
			  'last_name': g.name,
			  'first_name':''} 
				for g in db(db.groups.name.contains(qlist)).select(db.groups.ALL, orderby=db.groups.name)]}]

		taskteams = [] if not taskteams[0]['children'] else taskteams

		students = [] if not students else [{'text': 'Students', 'children':students}] 

		people = allfields +\
			gradefields +\
			taskteams +\
			students

	else:
		students = db().select(db.person.id, db.person.last_name, db.person.first_name, 
				orderby=db.person.last_name|db.person.first_name).as_list()
		people = [{'text': 'All', 'children':[{'id':'all_people', 'last_name':'All Students', 'first_name' : ''},
											  {'id':'all_leaders', 'last_name':'All Leaders', 'first_name' : ''}]}] +\
			[{'text': 'By Grade', 'children':[{'id':'grade_9', 'last_name': 'Freshmen', 'first_name': ''},
											  {'id':'grade_10', 'last_name': 'Sophomores', 'first_name': ''},
											  {'id':'grade_11', 'last_name': 'Juniors', 'first_name': ''},
											  {'id':'grade_12', 'last_name': 'Seniors', 'first_name': ''} ]}] +\
			[{'text': 'Task Teams', 'children': [{'id':'group_' + str(g.id), 
			  'last_name': g.name,
			  'first_name':''} 
				for g in db().select(db.groups.ALL, orderby=db.groups.name)]}] +\
			[{'text': 'Students', 'children':students}]

	return people

@auth.requires_login()
@auth.requires_membership('admin')
def call():
	"""Call function used when calling a function from an HTTP request"""
	return service()