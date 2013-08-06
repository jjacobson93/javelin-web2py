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

# @auth.requires_login()
# @service.json
# def attendance_sheet(kind):
# 	import tempfile
# 	import time
# 	from pyfpdf import FPDF, HTMLMixin

# 	class PDF(FPDF, HTMLMixin):
# 		pass

# 	io = None
# 	if kind == str(1): # Task Teams
# 		title = 'task_team_attendance'
# 		pages = list()
# 		# page_temp = """<h2>{}</h2>
# 		# 	<table border="1" width="100%>
# 		# 		<thead>
# 		# 			<tr>
# 		# 				<th width="10%">Student ID</th>
# 		# 				<th width="40%">Last Name</th>
# 		# 				<th width="40%">First Name</th>
# 		# 				<th width="10%>Cell Phone</th>
# 		# 			</tr>
# 		# 		</thead>
# 		# 		<tbody>
# 		# 			{}
# 		# 		</tbody>
# 		# 	</table>"""

# 		page_temp = """<h2>{}</h2><table border="0" align="center" width="50%">
# 		<thead><tr><th width="30%">Header 1</th><th width="70%">header 2</th></tr></thead>
# 		<tbody>
# 		<tr><td>cell 1</td><td>cell 2</td></tr>
# 		<tr><td>cell 2</td><td>cell 3</td></tr>
# 		</tbody>
# 		</table>
# 		"""

# 		teams = db().select(db.groups.ALL)
# 		for t in teams:
# 			tbody = list()
# 			students = db(db.group_rec.group_id==t.id).select(db.person.ALL,
# 				join=db.person.on(db.group_rec.person_id==db.person.id),
# 				orderby=[db.person.last_name, db.person.first_name])
# 			if students:
# 				for s in students:
# 					tbody.append("<tr><td>{}</td>" +\
# 						"<td>{}</td><td>{}</td>" +\
# 						"<td>{}</td></tr>".format(s.student_id, 
# 							s.last_name, s.first_name, s.cell_phone))

# 				pages.append(page_temp.format(t.name))

# 		pdf = PDF()
# 		for p in pages:
# 			pdf.add_page()
# 			pdf.write_html(p)

# 		temp = tempfile.NamedTemporaryFile(delete=True)
# 		pdf.output(temp, 'F')
# 		temp.file.seek(0)

# 	f = temp.file.read()
# 	temp.close()
# 	return f

# 	# filename = "{}_{}.pdf".format(title, int(time.time()))

# 	# file_id = db.file.insert(name=filename, file=db.file.file.store(io, filename))

# 	# db_file = db.file(file_id).file

# 	# return dict(filename=db_file)

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