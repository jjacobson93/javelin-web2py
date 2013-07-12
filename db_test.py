from gluon.dal import DAL, Field

db = DAL('postgres://postgres:p0stmast3r!@localhost/javelin', migrate=False)

db.define_table('person',
	Field('last_name', 'string', notnull=True),
	Field('first_name', 'string', notnull=True),
	Field('phone', 'string'),
	Field('home_phone', 'string'),
	Field('gender', 'string'),
	Field('email', 'string'),
	Field('street', 'string'),
	Field('city', 'string'),
	Field('state', 'string'),
	Field('zip_code', 'string'),
	Field('notes', 'string'),
	Field('pic', 'blob'))

db.define_table('groups',
	Field('name', 'string', notnull=True),
	Field('description', 'string'))

db.define_table('group_rec',
	Field('group_id', db.groups, notnull=True),
	Field('person_id', db.person, notnull=True),
	primarykey=['group_id', 'person_id'])