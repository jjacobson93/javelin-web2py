# from gluon import current
# from gluon.storage import Storage

# pydict = dict
# dict = Storage

# def api_query(f):
# 	def wrapper(*args, **vars):
# 		offset = int(vars.get('offset', -1))
# 		limit = int(vars.get('limit', -1))
# 		vars['limitby'] = (offset, offset + limit) if (offset != -1 and limit != -1) else (0, limit) if limit != -1 else None

# 		return f(*args, **vars)
# 	return wrapper

# class ApiModel(object):
# 	table = None

# 	@classmethod
# 	@api_query
# 	def find_all(cls):
# 		db = current.db
# 		result = dict()

# 	@classmethod
# 	def find_one(cls, **vars):
# 		db = current.db

# 		vars = {k: v for k, v in vars.items() if k not in ('offset', 'limit', 'limitby')}

# 		result = db[cls.table](**vars)
# 		return result

# 	@classmethod
# 	@api_query
# 	def find(cls, *args, **vars):
# 		db = current.db
# 		result = dict()

# 		id = args[0] if len(args) > 0 else None
# 		limitby = vars.get('limitby')
# 		query = (db[cls.table].id>0)
# 		for k, v in vars.items():
# 			if k not in ('offset', 'limit', 'limitby'):
# 				field = db[cls.table][k]
# 				if field.type == 'string':
# 					query = (query) & (field.contains(v))
# 				elif field.type == 'integer' or field.type == 'id':
# 					query = (query) & (field==v)


# 		result.data = db(query).select(limitby=limitby)
# 		result.status = 200

# 		return result


# class v1(object):

# 	class people(ApiModel):
# 		table = 'person'
		
# 	class groups(ApiModel):
# 		table = 'groups'

# 	class events(ApiModel):
# 		pass