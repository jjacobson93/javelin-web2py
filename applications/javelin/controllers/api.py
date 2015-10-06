from gluon.storage import Storage
from datetime import datetime
import re
pydict = dict
dict = Storage

extensions = ['json', 'xml']

result = dict(timestamp=request.utcnow.strftime("%Y-%m-%dT%H:%M:%S") + 'Z')

def accept_extensions(accepted):
	def outer(f):
		def inner(*args, **vars):
			accepted_extensions = accepted

			ext = vars.get('format')

			if ext != None and ext in accepted_extensions:
				request.extension = ext
			else:
				request.extension = 'json'

			response.view = 'api/default.' + request.extension

			return f(*args, **vars)
		return inner
	return outer

def api_query(f):
	def wrapper(*args, **vars):
		offset = int(vars.get('offset', -1))
		limit = int(vars.get('limit', -1))
		vars['limitby'] = (offset, offset + limit) if (offset != -1 and limit != -1) else (0, limit) if limit != -1 else None

		return f(*args, **vars)
	return wrapper

def __query_with_criteria(criteria):
	query = None
	for c in criteria:
		prop = c.get('property')
		verb = c.get('verb')
		value = c.get('value')
		subquery = None
		if prop and verb and value:
			# Graduation year
			if prop == 'grad_year':
				if verb == 'is equal to':
					subquery = db.person.grad_year==value
				elif verb == 'is between':
					if value[0] and value[1]:
						if value[0] < value[1]:
							subquery = (db.person.grad_year >= value[0])&(db.person.grad_year <= value[1])
						elif value[0] > value[1]:
							subquery = (db.person.grad_year <= value[0])&(db.person.grad_year >= value[1])
						else:
							subquery = (db.person.grad_year == value[0])
			# Course
			elif prop == 'course':
				if verb == 'is equal to':
					enrollment = [row.id for row in db(db.section.course_id==value['id']).select(db.person.id, join=[
						db.enrollment.on(db.person.id==db.enrollment.person_id),
						db.section.on(db.section.id==db.enrollment.section_id)
					])]

				elif verb == 'contains':
					enrollment = [row.id for row in db(db.course.title.contains(value)).select(db.person.id, join=[
						db.enrollment.on(db.person.id==db.enrollment.person_id),
						db.section.on(db.section.id==db.enrollment.section_id),
						db.course.on(db.course.id==db.section.course_id)
					])]

				subquery = db.person.id.belongs(enrollment)
			# Group membership
			elif prop == 'group_member':
				if verb == 'belonging to':
					membership = [row.id for row in db(db.group_member.group_id==value['id']).select(db.group_member.person_id)]
					subquery = db.person.id.belongs(membership)


			if subquery:
				query = query & subquery if query else subquery
		else:
			result.error = "Invalid criteria"
			response.status = 400
			break
	return query

@accept_extensions(extensions)
@request.restful()
def login():
	def POST(*args, **vars):
		username = vars.get('username')
		password = vars.get('password')
		auth.user = auth.login_bare(username, password)

		if auth.user:
			result.user = auth.user
		else:
			result.error = {'message': "Username and/or password was incorrect"}

		result.status = response.status
		return result

	return locals()


@auth.requires_login()
@request.restful()
def people():

	@api_query
	@accept_extensions(extensions)
	def GET(*args, **vars):
		"""
			patterns:
				/api/people
				/api/people/filter
				/api/people/:id
		"""

		id = None

		if len(args) > 1:
			response.status = 400
			result.status = response.status
			result.error = {'message': "Invalid request: Cannot have more than one argument. Only ID."}
			return result

		if len(args) > 0:
			try:
				id = int(args[0])
			except:
				id = None

		if id != None:
			data = db.person(id)
			user = db.auth_user(db.auth_user.person_id==id)
			course_instructor = db.instructor.with_alias('course_instructor')
			instructor = db.person.with_alias('instructor')


			enrollment = db(db.enrollment.person_id==id).select(
				# Section
				db.section.period, db.section.identifier,
				# Session
				db.session.name, db.session.year,
				# Course
				db.course.name, db.course.code,
				# Instructor
				instructor.last_name, instructor.first_name,
				join=[
					db.section.on(db.section.id==db.enrollment.section_id),
					db.session.on(db.session.id==db.section.session_id),
					db.course.on(db.course.id==db.section.course_id)
				],
				left=[
					course_instructor.on(course_instructor.section_id==db.section.id),
					instructor.on(instructor.id==course_instructor.person_id)
				],
				orderby=db.section.period).as_list()
			if user:
				data.user = dict(email=user.email)
			if enrollment:
				data.enrollment = enrollment

			result.data = data

		else:
			limitby = vars.get('limitby')
			search = vars.get('search')

			if search == None:
				query = (db.person.id>0)
				for k, v in vars.items():
					if k not in ('offset', 'limit', 'limitby', '_') and k in db.person:
						field = db.person[k]
						if field.type == 'string':
							query = (query) & (field.contains(v))
						elif field.type == 'integer' or field.type == 'id':
							query = (query) & (field==v)
			else:
				query = (db.person.last_name.contains(search))|(db.person.first_name.contains(search))

			result.data = []

			rows = db(query).select(left=db.auth_user.on(db.auth_user.person_id==db.person.id), limitby=limitby, orderby=db.person.id)
			for row in rows:
				new_dict = dict(phone_number=row.person.phone_number,
					picture=row.person.picture,
					first_name=row.person.first_name,
					last_name=row.person.last_name,
					grad_year=row.person.grad_year,
					student_id=row.person.student_id,
					id=row.person.id)

				if row.auth_user.id != None:
					new_dict.user = dict(email=row.auth_user.email)

				result.data.append(new_dict)

		result.status = response.status
		return result

	@accept_extensions(extensions)
	def POST(*args, **vars):
		is_filter = len(args) > 0 and args[0] == 'filter'

		if is_filter:
			criteria = vars.get('criteria')

			if criteria:
				query = __query_with_criteria(criteria)

				if 'error' not in result and query:
					result.data = db(query).select(db.person.id, db.person.last_name, db.person.first_name)
				elif 'error' not in result and not query:
					result.data = []

				print 'last sql:', db._lastsql

			# else:
			# 	result.error = "Cannot filter without criteria"
			# 	response.status = 400
			# for k, v in vars.items():
			# 	if k not in ('offset', 'limit', 'limitby') and k in db.person:
			# 		try:
			# 			prop, verb, val = v.split(',')
			# 		except:
			# 			result.error = "Malformed query"
			# 			response.status = 400
			# 			break

		else:
			try:
				data = db.person.validate_and_insert(**vars)
				if data['errors']:
					result.error = data['errors']
					response.status = 400
				else:
					result.data = db.person(data['id'])
					response.status = 201

			except (RuntimeError, AttributeError) as e:
				response.status = 400
				result.error = {'message': e.message}

		result.status = response.status
		return result

	@accept_extensions(extensions)
	def PUT(id, **vars):
		if id == None:
			response.status = 400
			result.error = {'message': 'ID must be included'}
			return result

		try:
			data = db(db.person.id==id).validate_and_update(**vars)
			if data['errors']:
				result.error = data['errors']
			else:
				result.data = db.person(id)

		except (RuntimeError, AttributeError, SyntaxError) as e:
			response.status = 400
			result.error = {'message': e.message}

		result.status = response.status
		return result

	@accept_extensions(extensions)
	def DELETE(*args, **vars):
		pass

	return locals()

@request.restful()
def groups():
	"""
		patterns:
			/api/groups/
			/api/groups?members=true
			/api/groups/:id 			
			/api/groups/:id/members		
	"""

	@api_query
	@accept_extensions(extensions)
	def GET(*args, **vars):

		if len(args) > 2:
			response.status = 400
			result.status = response.status
			result.error = {'message': "Invalid request: Cannot have more than two arguments. Only ID and 'members'."}
			return result

		id = args[0] if len(args) > 0 else None
		members = args[1] if len(args) > 1 else None
		limitby = vars.get('limitby')

		if id != None and members == None:
			result.data = db.groups(id)
		elif members != None and members != 'members':
			response.status = 400
			result.error = {'message': 'Invalid argument'}
		elif id != None and members != None and members == 'members':
			limitby = vars.get('limitby')

			query = (db.group_member.group_id==id)
			for k, v in vars.items():
				if k not in ('offset', 'limit', 'limitby'):
					query = (query) & (db.person[k].contains(v))

			data = dict()
			data.members = db(query).select(db.person.ALL, join=db.person.on(db.group_member.person_id==db.person.id))
			data.group = db.groups(id)
			result.data = data
		else:
			result.data = []
			groups_data = db(db.groups).select(limitby=limitby)
			if vars.get('members') == 'true':
				for i, group in enumerate(groups_data):
					data = dict(group.as_dict())
					if data.is_smart:
						query = __query_with_criteria(group.criteria)
						data.members = db(query).select(db.person.id, db.person.last_name, db.person.first_name)
					else:
						data.members = db(db.group_member.group_id==id).select(db.person.ALL, join=db.person.on(db.group_member.person_id==db.person.id))
					result.data.append(data)

		result.status = response.status
		return result

	@accept_extensions(extensions)
	def POST(*args, **vars):
		if len(args) == 0:
			try:
				data = db.groups.validate_and_insert(**vars)
				if data['errors']:
					result.error = data['errors']
					response.status = 400
				else:
					group = db.groups(data['id'])
					result.data = dict(group.as_dict())
					if result.data.is_smart:
						query = __query_with_criteria(group.criteria)
						result.data.members = db(query).select(db.person.id, db.person.last_name, db.person.first_name)
					else:
						result.data.members = db(db.group_member.group_id==id).select(db.person.ALL, join=db.person.on(db.group_member.person_id==db.person.id))
					response.status = 201
			except (RuntimeError, AttributeError) as e:
				result.error = {'message': e.message}
				response.status = 400

		elif len(args) == 2 and args[1] == 'members':
			try:
				group_id = int(args[0])
				person_id = int(vars.get('person_id', -1))
				exists = db((db.group_member.group_id==group_id)&(db.group_member.person_id==person_id)).count()

				if person_id != -1 and not exists:
					try:
						data = db.group_member.validate_and_insert(group_id=group_id, person_id=person_id)
						if data['errors']:
							result.error = data['errors']
							response.status = 400
						else:
							group_member = db.group_member(data['id'])
							result.data = dict()
							result.data.id = data['id']
							result.data.person = db.person(group_member.person_id)
							result.data.group = db.groups(group_member.group_id)

							response.status = 201
					except Exception as e:
						result.error = {'message': e.message}
						response.status = 400
				elif person_id != -1 and exists:
					response.status = 400
					result.error = {'message': 'person {} already exists in group {}'.format(person_id, group_id)}
				else:
					response.status = 400
					result.error = {'message': 'person_id is required'}

			except ValueError:
				result.error = {'message': '{} is not an integer'.format(args[0])}
				response.status = 400
		else:
			response.status = 400
			response.error = {'message': 'Invalid number of arguments.'}

		result.status = response.status
		return result

	@accept_extensions(extensions)
	def PUT(id, **vars):
		if id == None:
			response.status = 400
			result.error = {'message': 'ID must be included'}
			return result

		try:
			data = db(db.groups.id==id).validate_and_update(**vars)
			if data['errors']:
				result.error = data['errors']
			else:
				result.data = db.groups(id)

		except (RuntimeError, AttributeError, SyntaxError) as e:
			response.status = 400
			result.error = {'message': e.message}

		result.status = response.status
		return result

	@accept_extensions(extensions)
	def DELETE(*args, **vars):
		if len(args) != 1 and len(args) != 3:
			response.status = 400
			result.error = "DELETE requires an ID"
			return result
		elif len(args) == 1: # Delete group
			id = None
			try:
				id = int(args[0])
			except:
				pass
			if id:
				result.data = db(db.groups.id==id).delete()
			else:
				response.status = 400
				result.error = "Invalid ID. ID must be an integer: %s".format(args[0])
		elif len(args) == 3: # Delete member => /api/groups/:group_id/members/:person_id
			result.data = db((db.group_member.group_id==args[0])&(db.group_member.person_id==args[2])).delete()

		return result

	return locals()

@request.restful()
def events():

	@api_query
	@accept_extensions(extensions)
	def GET(*args, **vars):
		"""
			patterns:
				/api/events
				/api/events/:id
				/api/events?start=:start&end=:end
		"""

		if len(args) > 2:
			response.status = 400
			result.status = response.status
			result.error = {'message': "Invalid request: Cannot have more than two arguments. Only ID and 'attendance'."}
			return result

		id = args[0] if len(args) > 0 else None
		attendance = args[1] if len(args) > 1 else None
		limitby = vars.get('limitby')

		if id != None and attendance == None:
			result.data = db.events(id)
		elif attendance != None and attendance != 'attendance':
			response.status = 400
			result.error = {'message': 'Invalid argument'}
		elif id != None and attendance != None:
			limitby = vars.get('limitby')

			query = (db.attendance.event_id==id)
			# for k, v in vars.items():
			# 	if k not in ('offset', 'limit', 'limitby'):
			# 		query = (query) & (db.person[k].contains(v))

			data = dict()
			rows = db(query).select(db.attendance.attend_time, db.person.ALL, join=db.person.on(db.attendance.person_id==db.person.id))
			data.attendance = [dict(person=row.person, attend_time=row.attendance.attend_time) for row in rows]
			data.event = db.events(id)
			result.data = data
		else:
			start = int(vars.get('start', -1))
			end = int(vars.get('end', -1))
			if start != -1 and end != -1:
				start = datetime.fromtimestamp(start)
				end = datetime.fromtimestamp(end)

				data = db(db.events.is_recurring==False,
					( (db.events.start_time >= start) & (db.events.start_time < end) ) |
					( (db.events.end_time >= start) &  (db.events.end_time < end) ) |
					( (db.events.start_time <= start) & (db.events.end_time >= end) ) ).select(db.events.ALL, limitby=limitby)

				result.data = [dict(
					id=row.id,
					start=int(row.start_time.strftime('%s')) if row.start_time else None,
					end=int(row.end_time.strftime('%s')) if row.end_time else None,
					title=row.title, 
					notes=row.notes,
					location=row.location,
					allDay=row.is_all_day,
					is_recurring=row.is_recurring,
					end_recurring=row.end_recurring) for row in data]
			else:
				result.data = db(db.events).select(limitby=limitby)

		result.status = response.status
		return result

	@accept_extensions(extensions)
	def POST(*args, **vars):
		if len(args) == 0:
			try:
				data = db.events.validate_and_insert(**vars)
				if data['errors']:
					result.error = data['errors']
					response.status = 400
				else:
					result.data = db.events(data['id'])
					response.status = 201
			except (RuntimeError, AttributeError) as e:
				result.error = {'message': e.message}
				response.status = 400
		elif len(args) == 2 and args[1] == 'attendance':
			try:
				event_id = int(args[0])
				person_id = int(vars.get('person_id', -1))
				exists = db((db.attendance.event_id==event_id)&(db.attendance.person_id==person_id)).count()

				if person_id != -1 and not exists:
					try:
						data = db.attendance.validate_and_insert(event_id=event_id, person_id=person_id, attend_time=request.utcnow)
						if data['errors']:
							result.error = data['errors']
							response.status = 400
						else:
							attendance = db.attendance(data['id'])
							result.data = dict()
							result.data.id = data['id']
							result.data.person = db.person(attendance.person_id)
							result.data.event = db.events(attendance.event_id)
							result.data.attend_time = attendance.attend_time

							response.status = 201
					except Exception as e:
						result.error = {'message': e.message, 'vars': {'person_id': person_id, 'event_id': event_id}}
						response.status = 400
				elif person_id != -1 and exists:
					response.status = 400
					result.error = {'message': 'person {} already exists in event {}'.format(person_id, event_id)}
				else:
					response.status = 400
					result.error = {'message': 'person_id is required'}

			except ValueError:
				result.error = {'message': '{} is not an integer'.format(args[0])}
				response.status = 400
		else:
			response.status = 400
			response.error = {'message': 'Invalid number of arguments.'}

		result.status = response.status
		return result

		return result

	@accept_extensions(extensions)
	def PUT(*args, **vars):
		id = args[0] if len(args) > 0 else None

		if id == None:
			response.status = 400
			result.error = {'message': 'ID must be included'}
			return result

		try:
			data = db(db.events.id==id).validate_and_update(**vars)
			if data['errors']:
				result.error = data['errors']
			else:
				result.data = db.groups(id)

		except (RuntimeError, AttributeError, SyntaxError) as e:
			response.status = 400
			result.error = {'message': e.message}

		result.status = response.status
		return result

	@accept_extensions(extensions)
	def DELETE(*args, **vars):
		if len(args) != 1 and len(args) != 3:
			response.status = 400
			result.error = {'message': "DELETE requires an ID"}
			return result
		elif len(args) == 1: # Delete event
			result.data = db(db.events.id==args[0]).delete()
		elif len(args) == 3: # Delete attendance => /api/events/:event_id/attendance/:person_id
			result.data = db((db.attendance.event_id==args[0])&(db.attendance.person_id==args[2])).delete()

		return result

	return locals()

@request.restful()
def courses():

	@api_query
	@accept_extensions(extensions)
	def GET(*args, **vars):
		"""
			/api/courses/
			/api/courses/:id
			/api/courses/:id/sections
			/api/courses/:id/sections/enrollment
		"""
		if len(args) == 0:
			limitby = vars.get('limitby')
			result.data = [
				dict(id=row.course.id, code=row.course.code, name=row.course.name,
					 department=row.department)
					for row in db(db.course).select(join=db.department.on(db.department.id==db.course.department_id), limitby=limitby)]
		elif len(args) > 0 and len(args) < 4:

			# Check for a valid integer id
			try:
				id = int(args[0])
			except ValueError:
				id = None
				response.status = 400
				result.error = {'message': 'Invalid ID: ' + args[0]}

			if id != None:
				# Get the course
				row = db(db.course.id==id).select(join=db.department.on(db.department.id==db.course.department_id)).first()

				if row:
					# Get data
					result.data = dict(id=row.course.id, code=row.course.code, name=row.course.name, department=row.department)

					# Sections
					if len(args) > 1 and args[1] == 'sections':

						query = (db.section.course_id==id)&(db.session.id==db.section.session_id)
						# Per session
						session = vars.get('session')

						subquery = None
						if session != None:
							sessions = session.split(',')
							if sessions and sessions[0]:
								for sess in sessions:
									try:
										name, year = sess.split('_')
										sess_query = ((db.session.name==name)&(db.session.year==year))
										subquery = subquery | sess_query if subquery else sess_query
									except ValueError:
										result.data = None
										response.status = 400
										result.error = {'message': 'Invalid request'}
										break


						if result.data != None:
							if subquery != None:
								query = query & subquery

							course_instructor = db.instructor.with_alias('course_instructor')
							instructor = db.person.with_alias('instructor')
							result.data.sections = [
								dict(id=row.section.id, period=row.section.period, identifier=row.section.identifier,
									 session=row.session, instructor=row.instructor)
									for row in db(query).select(
										db.section.ALL, db.session.ALL, instructor.id, 
										instructor.last_name, instructor.first_name,
										join=[
											course_instructor.on(course_instructor.section_id==db.section.id),
											instructor.on(instructor.id==course_instructor.person_id)
										])]

							# Enrollment
							for section in result.data.sections:
								section.enrollment = [row.person_id for row in db(db.enrollment.section_id==section.id).select(db.enrollment.person_id)]

						else:
							del result.data


					elif len(args) > 1 and args[1] != 'sections':
						response.status = 400
						result.error = {'message': 'Invalid argument: ' + args[1]}
						del result.data
				else:
					result.data = None
		else:
			response.status = 400
			result.error = {'message': 'Invalid number of arguments: {}'.format(len(args))}



		result.status = response.status
		return result

	return locals()


# @request.restful()
# def sections():

# 	@api_query
# 	@accept_extensions(extensions)
# 	def GET(*args, **vars):
# 		"""
# 			/api/sections/
# 			/api/sections/:id
# 			/api/sections/:id/enrollment
# 		"""

# 	return locals()

@request.restful()
def tutoring():

	@api_query
	@accept_extensions(extensions)
	def GET(*args, **vars):
		"""
			/api/tutoring/subjects
		"""
		if len(args) == 1 and args[0] == 'subjects':
			result.data = db(db.tutoring_subject).select()
		else:
			response.status = 400

		result.status = response.status
		return result

	@accept_extensions(extensions)
	def POST(*args, **vars):
		if len(args) == 1 and args[0] == 'subjects':
			try:
				data = db.tutoring_subject.validate_and_insert(**vars)
				if data['errors']:
					result.error = data['errors']
					response.status = 400
				else:
					result.data = db.tutoring_subject(data['id'])
					response.status = 201
			except (RuntimeError, AttributeError) as e:
				result.error = {'message': e.message}
				response.status = 400
		else:
			response.status = 400

		result.status = response.status
		return result

	return locals()

@request.restful()
def search():

	@api_query
	@accept_extensions(extensions)
	def GET(*args, **vars):
		query = vars.get('query', '')
		people = db((db.person.last_name.contains(query))|db.person.first_name.contains(query)).select(db.person.id, db.person.last_name, db.person.first_name)
		groups = db((db.groups.name.contains(query))|db.groups.description.contains(query)).select(db.groups.id, db.groups.name, db.groups.description)
		events = db((db.events.title.contains(query))|db.events.notes.contains(query)).select(db.events.id, db.events.title, db.events.notes)

		result.data = dict(people=people, groups=groups, events=events)
		return result

	return locals()