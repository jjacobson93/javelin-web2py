# -*- coding: utf-8 -*-
"""
	Javelin Web2Py Admin Controller
"""

# metadata
__author__ = "Jeremy Jacobson"
__copyright__ = "(c) 2013, Jacobson and Varni, LLC"
__date__ = "7/12/2013"
__email__ = "jjacobson93@gmail.com"
__data__ = {'name' : 'jadmin', 'label' : 'Admin', 'description' : 'Only accessible to admins', 
	'icon' : 'briefcase', 'u-icon' : u'\uf0b1', 'color':'orange', 'required' : True}

import time
from datetime import datetime
from applications.javelin.ctr_data import ctr_enabled, get_ctr_data
from gluon.contrib import simplejson as json
from gluon.tools import Service
from gluon.storage import Storage
service = Service(globals())

DOC_TYPES = Storage(
	CALLSLIP=Storage(value=0, label="Call Slips"),
	ATTSHEETS=Storage(value=1, label="Attendance Sheets"),
	NAMETAGS=Storage(value=2, label="Nametags")
)

@auth.requires_login()
@auth.requires_membership('admin')
def index():
	"""Loads the index page for the 'Admin' controller

	:returns: a dictionary to pass to the view with the list of ctr_enabled and the active module ('admin')
	"""
	ctr_data = get_ctr_data()
	users = db().select(db.auth_user.ALL)
	approvals = db(db.auth_user.registration_key=='pending').select(db.auth_user.ALL)
	return dict(ctr_enabled=ctr_enabled, ctr_data=ctr_data, active_module='jadmin', users=users, approvals=approvals, doctypes=DOC_TYPES)

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
						join=db.course_rec.on((db.course.id==db.course_rec.course_id) & (db.course_rec.student_id==pid)),
						orderby=db.course.period)]
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

		centerStyle = ParagraphStyle(name='Center', alignment=TA_CENTER)
		leftStyle = ParagraphStyle(name='Left', alignment=TA_LEFT)
		tableStyle = TableStyle([('VALIGN',(0,-1),(-1,-1),'TOP')])
		label_num = 0
		row_num = 0
		labels = list()

		for pid in persons:
			row = db(db.person.id==pid).select(db.person.ALL).first()

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

			firstName = Paragraph("<font face='Times-Bold' size=18>{}</font>".format(row.first_name), centerStyle)
			label.append(firstName)
			label.append(Spacer(1, 11))

			lastName = Paragraph("<font face='Times-Roman' size=11>{}</font>".format(row.last_name), centerStyle)
			label.append(lastName)
			label.append(Spacer(1,20))

			# if row.crew.wefsk != '' or row.crew.wefsk != None or row.crew.wefsk != 'N/A':
			# 	try:
			# 		rooms = rotation(row.crew.wefsk.split('-')[0], row.crew.wefsk.split('-')[1])
			# 	except:
			# 		rooms = 'N/A'
			# else:
			# 	rooms = 'N/A'

			label.append(Paragraph("<font face='Times-Roman' size=11>ID#: {}</font>".format(row.student_id), leftStyle))
			label.append(Paragraph("<font face='Times-Roman' size=11>Crew #: {}</font>".format(row.crew), leftStyle))

			# label.append(Paragraph("<font face='Times-Roman' size=11>Crew Room: {}</font>".format(row.crew.room), leftStyle))
			# label.append(Paragraph("<font face='Times-Roman' size=11>W.E.F.S.K. Rotation: {}</font>".format(rooms), leftStyle))

			labels.append(label)

			if label_num == 0:
				labels.append(Spacer(14, 144))

			label_num += 1

		doc_title = '_'.join(event_name.split())


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
	names = json.loads(names)
	response = []
	for name in names:
		r = db.module_names.update_or_insert(name=name['name'], label=name['value'])
		response.append(r)

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
	response = list()

	lines = csv_file.rstrip().splitlines()

	if len(lines) > 0:
		columns = lines.pop(0).split(',')

		for i in range(len(columns)):
			columns[i] = '_'.join(columns[i].lower().split())

		for line in lines:
			record = dict()
			line = line.split(',')
			for i in range(len(line)):
				record[columns[i]] = line[i]

			record = dict((k,v) for k,v in record.items() if k in db.person.fields)
			response.append(db.person.update_or_insert(db.person.id==record['id'], **record))

	return dict(response=response)

@auth.requires_login()
@auth.requires_membership('admin')
@service.json
def import_from_query(csv_file, leaders):
	"""Imports records into the database from a CSV file (in the form of the queries from VHS)

	:param file: the file to be imported
	:returns: a dictionary with a response, either a 0 or 1, depending on success
	"""
	import csv
	import StringIO

	leaders = True if leaders=="true" else False

	def phone_format(n):
		try:
			return format(int(n[:-1]), ",").replace(",", "-") + n[-1]
		except:
			return None

	if not leaders:

		file_string = StringIO.StringIO(csv_file)
		lines = list(csv.reader(file_string, skipinitialspace=True))
		del file_string
		del csv_file

		# INSERT STUDENTS

		student_ids = list()
		teacher_ids = list()
		course_ids = list()

		columns = lines.pop(0)

		while len(lines) > 0:
			record = dict()

			line = lines.pop(0)

			student_id = line[columns.index('student_id')]
			teacher_id = line[columns.index('teacher_id')]
			course_id = line[columns.index('course_id')]

			if student_id and student_id not in student_ids:
				student_ids.append(student_id)

				for i in range(len(line)):
					record[columns[i]] = line[i]

				record = dict((k,v) for k,v in record.items() if k in db.person.fields)
				if record.get('cell_phone', None):
					record['cell_phone'] = phone_format(record['cell_phone'])
				if record.get('home_phone', None):
					record['home_phone'] = phone_format(record['home_phone'])

				db.person.update_or_insert(db.person.student_id==student_id, **record)

			if teacher_id and teacher_id not in teacher_ids:
				teacher_ids.append(teacher_id)
				db.teacher.update_or_insert(db.teacher.teacher_id==teacher_id, **{
					'teacher_id':line[columns.index('teacher_id')],
					'teacher_name':line[columns.index('teacher_name')]})

			if course_id and teacher_id and course_id not in course_ids:
				course_ids.append(course_id)
				teacher = db(db.teacher.teacher_id==teacher_id).select(db.teacher.id).first()
				if teacher:
					db.course.update_or_insert(db.course.course_id==course_id, **{
						'course_id':line[columns.index('course_id')],
						'code':line[columns.index('course_code')],
						'title':line[columns.index('course_title')],
						'period':line[columns.index('period')],
						'room':line[columns.index('room')],
						'teacher_id':teacher.id})

			if course_id and student_id:
				course = db(db.course.course_id==course_id).select().first()
				student = db(db.person.student_id==student_id).select().first()
				if course and student:
					db.course_rec.update_or_insert((db.course_rec.course_id==course.id) & 
						(db.course_rec.student_id==student.id), 
						course_id=course.id, 
						student_id=student.id)

			db.commit()
			del record
			del line

		return dict(response=True)
		
	else:
		errors = list()
		lines = list(csv.reader(StringIO.StringIO(csv_file), skipinitialspace=True))

		columns = lines.pop(0)

		short_tasks = {
			'Team Sacrifice (Must have a car and willingness to work later than others)' : 'Team Sacrifice',
			"Peer Support (Must be enrolled in Mr. Ward's Psychology or Peer Support class)" : 'Peer Support',
			"Tutor/Study Buddy (Academic credits are available for this option)" : 'Tutor/Study Buddy',
			"Database Manager (Must know Excel, Mail merge, and other technologies)" : 'Database Manager',
			"Facebook Maintenance (You are responsible for up keeping on our page. Must be a FB addict)" : "Facebook Maintenance",
			"Fundraising Team" : "Fundraising Team",
			"TAs (Work with freshmen and Mr. Varni, Mr. Ward, or Mrs. Housley during the school day (Academic credits are available for this option)": "TAs",
			"Posters & Propaganda" : "Posters & Propaganda",
			"Public Outreach (Attend Parent Night, Back-to-School, other public events)" : 'Public Outreach',
			"ASB Support (Those enrolled in 4th period Leadership class should check this option, but others are welcome as well)" : "ASB Support",
			"L.O.C.s (Loyal Order of the Crushers. Attend home athletic and extracurricular events)": "L.O.C.s",
			"Dirty 30 (Explain various aspects of high school culture to freshmen on Orientation Day afternoon)" : "Dirty 30",
			"Set-up (Room Mapping) and Clean-up (Orientation Day only)": "Set-up and Clean-up",
			"Homecoming Parade (Dress up and ride on our float! Easy!)" : "Homecoming Parade",
			"Security/Safety (Helps keep freshmen in line; works with Peer Support on Orientation Day)": "Security/Safety",
			"Food Prep & Clean-up (Orientation Day only)": "Food Prep & Clean-up",
			"Fashion (Make costumes for House Hotties and Homecoming Parade)" : "Fashion",
			'Burgundy Beauties and Golden Guns (Formerly "House Hotties")' : "Burgundy Beauties and Golden Guns",
			"Audio-Visual (Responsible for music and videos during Orientation)" : "Audio-Visual",
			"A-Team (Alumni only)": "A-Team"
		}

		task_teams = [task.name for task in db().select(db.groups.name)]

		for line in lines:
			record = dict()

			for i in range(len(line)):
				if columns[i] == 'last_name' or columns[i] == 'first_name':
					line[i] = line[i].capitalize()

				record[columns[i]] = line[i]

			record = dict((k,v) for k,v in record.items() if k in db.person.fields)

			if record.get('cell_phone', None):
				record['cell_phone'] = phone_format(record['cell_phone'])

			try:
				person = db((db.person.last_name==record['last_name']) & 
					(db.person.first_name==record['first_name'])).select(db.person.ALL).first()
				if person:
					person_id = person.id

					db(db.person.id==person_id).update(**record)
					db(db.person.id==person_id).update(leader=True)

					aTasks = line[columns.index('a_tasks')].split(',')
					bTasks = line[columns.index('b_tasks')].split(',')
					cTasks = line[columns.index('c_tasks')].split(',')

					tasks_to_add = list()
					for task in aTasks:
						if task not in task_teams and task in short_tasks.values():
							task_id = db.groups.insert(name=task)
							tasks_to_add.append(task_id)
							task_teams.append(task)
						elif task in task_teams and task in short_tasks.values():
							task_row = db(db.groups.name==task).select().first()
							if task_row:
								task_id = task_row.id
								tasks_to_add.append(task_id)


					for task in bTasks:
						if task not in task_teams and task in short_tasks.values():
							task_id = db.groups.insert(name=task)
							tasks_to_add.append(task_id)
							task_teams.append(task)
						elif task in task_teams and task in short_tasks.values():
							task_row = db(db.groups.name==task).select().first()
							if task_row:
								task_id = task_row.id
								tasks_to_add.append(task_id)

					for task in cTasks:
						if task not in task_teams and task in short_tasks.values():
							task_id = db.groups.insert(name=task)
							tasks_to_add.append(task_id)
							task_teams.append(task)
						elif task in task_teams and task in short_tasks.values():
							task_row = db(db.groups.name==task).select().first()
							if task_row:
								task_id = task_row.id
								tasks_to_add.append(task_id)

					for task in tasks_to_add:
						if not db((db.group_rec.group_id==task_id) & (db.group_rec.person_id==person_id)).select().first():
							db.group_rec.insert(group_id=task_id, person_id=person_id)
			except:
				errors.append(record['last_name'] + ", " + record['first_name'])

		return dict(errors=errors)

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