# -*- coding: utf-8 -*-

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()
from gluon import current
import phonenumbers

# import psycopg2
# from gluon.dal import PostgresAdapter
# PostgresAdapter.driver = psycopg2

db = DAL('postgres://jjacobson:test@localhost/javelin',pool_size=1,check_reserved=['postgres'])
current.db = db

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'
## (optional) static assets folder versioning
# response.static_version = '0.0.0'

from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
auth = Auth(db)
crud, service, plugins = Crud(db), Service(), PluginManager()

## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' or 'smtp.gmail.com:587'
mail.settings.sender = 'you@gmail.com'
mail.settings.login = 'username:password'

## configure auth policy
# auth.settings.login_url = URL('default', 'index', anchor='/login')

auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True
auth.settings.remember_me_form = False
auth.settings.register_verify_password = False

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)

from javelin_utils import IS_PHONE_NUMBER, IS_ALPHA

db.define_table('person',
	Field('student_id', 'integer'),
	Field('last_name', 'string', notnull=True, required=True, requires=IS_ALPHA()),
	Field('first_name', 'string', notnull=True, required=True, requires=IS_ALPHA()),
	Field('sex', 'string', requires=IS_IN_SET(['M', 'F'])),
	Field('grad_year', 'integer'),
	Field('address', 'string'),
	Field('city', 'string'),
	Field('state', 'string'),
	Field('zip_code', 'string'),
	Field('phone_number', 'string', requires=IS_EMPTY_OR(IS_PHONE_NUMBER())),
	Field('cell_number', 'string', requires=IS_EMPTY_OR(IS_PHONE_NUMBER())),
	Field('email', 'string'),
	Field('picture', 'upload'))

auth.settings.extra_fields['auth_user'] = [
	Field('person_id', 'reference person', requires=IS_IN_DB(db, db.person, '%(last_name)s, %(first_name)s'))
]

## create all tables needed by auth if not custom tables
auth.define_tables(username=False, signature=False)

db.define_table('groups',
	Field('name', 'string', notnull=True, required=True, unique=True),
	Field('description', 'text'),
	Field('permission', 'string', notnull=True, required=True, requires=IS_IN_SET(['user', 'admin', 'teachers', 'all'])),
	Field('is_smart', 'boolean', notnull=True, default=False),
	Field('criteria', 'json'))

db.define_table('group_member',
	Field('group_id', 'reference groups', notnull=True, required=True, requires=IS_IN_DB(db, db.groups, '%(name)s')),
	Field('person_id', 'reference person', notnull=True, required=True, requires=IS_IN_DB(db, db.person, '%(last_name)s, %(first_name)s')))

db.define_table('events',
	Field('title', 'string', notnull=True, required=True),
	Field('notes', 'text'),
	Field('location', 'text'),
	Field('start_time', 'datetime', notnull=True, required=True),
	Field('end_time', 'datetime', notnull=True, required=True),
	Field('is_all_day', 'boolean', default=False),
	Field('is_recurring', 'boolean', default=False),
	Field('end_recurring', 'datetime'))

db.define_table('attendance',
	Field('event_id', 'reference events', notnull=True, required=True, requires=IS_IN_DB(db, db.events, '%(title)s')),
	Field('person_id', 'reference person', notnull=True, required=True, requires=IS_IN_DB(db, db.person, '%(last_name)s, %(first_name)s')),
	Field('attend_time', 'datetime'), notnull=True, required=True, default=request.utcnow)

# SCHOOL SPECIFIC
db.define_table('department', 
	Field('name', 'string', notnull=True, required=True))

db.define_table('course',
	Field('name', 'string', notnull=True, required=True),
	Field('code', 'string', notnull=True, required=True),
	Field('department_id', 'reference department', notnull=True, required=True, requires=IS_IN_DB(db, db.department, '%(name)s')),
	format='%(name)s (%(code)s)')

db.define_table('session',
	Field('name', 'string', notnull=True, required=True, requires=IS_IN_SET(['Winter', 'Spring', 'Summer', 'Fall'])),
	Field('year', 'integer', notnull=True, required=True))

db.define_table('section',
	Field('identifier', 'integer'),
	Field('period', 'integer'),
	Field('course_id', 'reference course', notnull=True, required=True, requires=IS_IN_DB(db, db.course, '%(name)s (%(code)s)')),
	Field('session_id', 'reference session', notnull=True, required=True, requires=IS_IN_DB(db, db.session, '%(name)s %(year)s')))

db.define_table('enrollment',
	Field('person_id', 'reference person', notnull=True, required=True, requires=IS_IN_DB(db, db.person, '%(last_name)s, %(first_name)s')),
	Field('section_id', 'reference section', notnull=True, required=True, requires=IS_IN_DB(db, db.section)))

db.define_table('instructor',
	Field('person_id', 'reference person', notnull=True, required=True, requires=IS_IN_DB(db, db.person, '%(last_name)s, %(first_name)s')),
	Field('section_id', 'reference section', notnull=True, required=True, requires=IS_IN_DB(db, db.section)))
	
db.define_table('transcript',
	Field('enrollment_id', 'reference enrollment', notnull=True, required=True),
	Field('first_grade', 'string'),
	Field('second_grade', 'string'),
	Field('final_grade', 'string'))

db.define_table('tutoring_subject',
	Field('title', 'string', notnull=True, required=True),
	Field('department_id', 'reference department'))

db.define_table('tutoring_attendance',
	Field('person_id', 'reference person'),
	Field('subject_id', 'reference tutoring_subject'))