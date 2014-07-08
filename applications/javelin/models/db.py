# -*- coding: utf-8 -*-

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()
from gluon import current
import phonenumbers

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
	Field('student_id', 'integer', notnull=True, required=True),
	Field('last_name', 'string', notnull=True, required=True, requires=IS_ALPHA()),
	Field('first_name', 'string', notnull=True, required=True, requires=IS_ALPHA()),
	Field('grade', 'integer', default=0),
	Field('phone_number', 'string', requires=IS_PHONE_NUMBER()),
	Field('picture', 'upload'))

auth.settings.extra_fields['auth_user'] = [
	Field('person_id', 'reference person', requires=IS_IN_DB(db, db.person, '%(last_name)s, %(first_name)s'))
]

## create all tables needed by auth if not custom tables
auth.define_tables(username=False, signature=False)

db.define_table('groups',
	Field('name', 'string', notnull=True, required=True, unique=True),
	Field('description', 'text'))

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

# from gluon.dal import Rows
# from javelin_utils import resolve_refs
# Rows.resolve_refs = resolve_refs

# from api import v1 as api