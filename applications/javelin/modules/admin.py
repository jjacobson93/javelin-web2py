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

def import_from_query(csv_file):
	db = current.javelin.db

	def phone_format(n):
		return format(int(n[:-1]), ",").replace(",", "-") + n[-1]

	lines = csv_file.rstrip().splitlines()

	# INSERT STUDENTS

	ids = list()

	columns = lines.pop(0).split(',')
	for i in range(len(columns)):
		columns[i] = '_'.join(columns[i].lower().split())

	for i in range(1,len(lines)):
		record = dict()
		line = lines[i].rstrip().split(',')
		for i in range(len(line)):
			record[columns[i]] = line[i]

		record = dict((k,v) for k,v in record.items() if k in db.person.fields)
		if record.get('cell_phone', None):
			record['cell_phone'] = phone_format(record['cell_phone'])
		if record.get('home_phone', None):
			record['home_phone'] = phone_format(record['home_phone'])
			
		if record['student_id'] and record['student_id'] not in ids:
			ids.append(record['student_id'])
			db.person.update_or_insert(db.person.student_id==record['student_id'], **record)

	# INSERT TEACHERS

	ids = list()
	lines.pop(0)
	for line in lines:
		line = line.rstrip().split(',')
		currid = line[13]
		if currid and currid not in ids:
			ids.append(currid)
			db.teacher.update_or_insert(db.teacher.teacher_id==currid, **{
				'teacher_id':line[13],
				'teacher_name':line[14]})

	# INSERT COURSES

	ids = list()
	lines.pop(0)
	for line in lines:
		line = line.rstrip().split(',')
		currid = line[15]
		if currid and currid not in ids:
			ids.append(currid)
			db.course.update_or_insert(db.course.course_id==currid, **{
				'course_id':line[15],
				'code':line[10],
				'title':line[11],
				'period':line[12],
				'teacher_id':db(db.teacher.teacher_id==line[13]).select(db.teacher.id).first().id})

	# INSERT COURSE_RECS

	for line in lines:
		line = line.rstrip().split(',')
		course_id = line[15]
		student_id = line[0]
		if course_id and student_id:
			db.course_rec.update_or_insert((db.course_rec.course_id==course_id) & 
				(db.course_rec.student_id==student_id), 
				course_id=db(db.course.course_id==course_id).select(db.course.id).first().id, 
				student_id=db(db.person.student_id==student_id).select(db.person.id).first().id)

	return dict(response=True)
	