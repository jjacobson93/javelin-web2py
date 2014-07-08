from gluon.storage import Storage
from datetime import datetime
import re
pydict = dict
dict = Storage

extensions = ['json', 'xml']

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


result = dict(timestamp=request.utcnow.strftime("%Y-%m-%dT%H:%M:%S") + 'Z')

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
				/api/people/:id
		"""

		if len(args) > 1:
			response.status = 400
			result.status = response.status
			result.error = {'message': "Invalid request: Cannot have more than one argument. Only ID."}
			return result

		id = args[0] if len(args) > 0 else None
		if id != None:

			data = db.person(id)
			user = db.auth_user(db.auth_user.person_id==id)
			if user:
				data.user = dict(email=user.email)

			result.data = data
		else:
			limitby = vars.get('limitby')

			query = (db.person.id>0)
			for k, v in vars.items():
				if k not in ('offset', 'limit', 'limitby'):
					field = db.person[k]
					if field.type == 'string':
						query = (query) & (field.contains(v))
					elif field.type == 'integer' or field.type == 'id':
						query = (query) & (field==v)

			result.data = [dict(
				user=dict(email=row.auth_user.email),
				phone_number=row.person.phone_number,
				picture=row.person.picture,
				first_name=row.person.first_name,
				last_name=row.person.last_name,
				grade=row.person.grade,
				id=row.person.id) if row.auth_user.id != None else row.person for row in db(query).select(left=db.auth_user.on(db.auth_user.person_id==db.person.id), limitby=limitby)]

		result.status = response.status
		return result

	@accept_extensions(extensions)
	def POST(*args, **vars):
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
			result.data = db(db.groups).select(limitby=limitby)

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
					result.data = db.groups(data['id'])
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
			result.data = db(db.groups.id==args[0]).delete()
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