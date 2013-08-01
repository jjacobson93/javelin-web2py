# -*- coding: utf-8 -*-
"""
	Javelin Web2Py Admin Module
"""

# metadata
__author__ = "Jeremy Jacobson"
__copyright__ = "(c) 2013, Jacobson and Varni, LLC"
__date__ = "7/12/2013"
__email__ = "jjacobson93@gmail.com"
__data__ = {'name' : 'jadmin', 'label' : 'Admin', 'description' : 'Only accessible to admins', 
	'icon' : 'briefcase', 'u-icon' : u'\uf0b1', 'required' : True}

from globals import current

def update_names(names):
	db = current.javelin.db

	response = []
	for name in names:
		r = db.module_names.update_or_insert(name=name['name'], label=name['value'])
		response.append(r)

	return response

def import_from_csv(csv_file, contains_ids):
	db = current.javelin.db

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

def import_from_query(csv_file, leaders):
	import csv
	import StringIO

	db = current.javelin.db

	def phone_format(n):
		try:
			return format(int(n[:-1]), ",").replace(",", "-") + n[-1]
		except:
			return None

	if not leaders:

		lines = list(csv.reader(StringIO.StringIO(csv_file), skipinitialspace=True))

		# INSERT STUDENTS

		student_ids = list()
		teacher_ids = list()
		course_ids = list()

		columns = lines.pop(0)

		for line in lines:
			record = dict()

			student_id = line[0]
			teacher_id = line[13]
			course_id = line[15]

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
					'teacher_id':line[13],
					'teacher_name':line[14]})

			if course_id and teacher_id and course_id not in course_ids:
				course_ids.append(course_id)
				teacher = db(db.teacher.teacher_id==teacher_id).select(db.teacher.id).first()
				if teacher:
					db.course.update_or_insert(db.course.course_id==course_id, **{
						'course_id':line[15],
						'code':line[10],
						'title':line[11],
						'period':line[12],
						'teacher_id':teacher.id})

			if course_id and student_id:
				course = db(db.course.course_id==course_id).select().first()
				student = db(db.person.student_id==student_id).select().first()
				if course and student:
					db.course_rec.update_or_insert((db.course_rec.course_id==course.id) & 
						(db.course_rec.student_id==student.id), 
						course_id=course.id, 
						student_id=student.id)

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
	