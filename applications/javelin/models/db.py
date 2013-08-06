# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

import logging
logger = logging.getLogger('web2py.app.javelin')
logger.setLevel(logging.DEBUG)

from gluon.custom_import import track_changes
track_changes(True)

if not request.env.web2py_runtime_gae:
	## if NOT running on Google App Engine use SQLite or other DB
	# db = DAL('sqlite://storage.sqlite',pool_size=1,check_reserved=['all'],migrate=False)
	db = DAL('postgres://postgres:p0stmast3r!@localhost/javelin')
	session.connect(request, response, db=db, masterapp=None)
else:
	## connect to Google BigTable (optional 'google:datastore://namespace')
	db = DAL('google:datastore')
	## store sessions and tickets there
	session.connect(request, response, db=db)
	## or store session in Memcache, Redis, etc.
	## from gluon.contrib.memdb import MEMDB
	## from google.appengine.api.memcache import Client
	## session.connect(request, response, db = MEMDB(Client()))

from globals import current
from gluon.storage import Storage
current.javelin = Storage()
current.javelin.db = db

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
auth = Auth(db)
crud, service, plugins = Crud(db), Service(), PluginManager()

## add field for user.active
auth.settings.extra_fields['auth_user'] = [Field('active', 'boolean', default=True)]

## create all tables needed by auth if not custom tables
auth.define_tables(username=True, signature=False)

## configure email
mail = auth.settings.mailer
mail.settings.server = 'smtp.gmail.com:587'
mail.settings.sender = 'vc2messager@gmail.com'
mail.settings.login = 'vc2messager:akwpyddynlbfrhzt'

current.javelin.mail = mail

# Replace user, password, server and port in the connection string
# Set port as 993 for SSL support
# imapdb = DAL("imap://vc2messager:srivijaya@imap.gmail.com:993", pool_size=1)
# imapdb.define_tables()

## configure auth policy
auth.settings.registration_requires_verification = True
auth.settings.registration_requires_approval = True
auth.settings.reset_password_requires_verification = True
auth.settings.register_fields=['first_name', 'last_name', 'email', 'username', 'password']
auth.settings.profile_fields=['first_name', 'last_name', 'email', 'username']
auth.settings.hmac_key = "sha512:93b42428-33e2-4c1d-bfa0-2de193983bd8"

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
from gluon.contrib.login_methods.rpx_account import use_janrain
use_janrain(auth, filename='private/janrain.key')

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

db.define_table('crew',
	Field('room', 'string'),
	Field('wefsk', 'string'))

db.define_table('person',
	Field('student_id', 'integer', notnull=True, unique=True),
	Field('last_name', 'string', notnull=True, required=True),
	Field('first_name', 'string', notnull=True, required=True),
	Field('home_phone', 'string'),
	Field('cell_phone', 'string'),
	Field('cell_provider', 'string'),
	Field('gender', 'string'),
	Field('email', 'string'),
	Field('street', 'string'),
	Field('city', 'string'),
	Field('state', 'string'),
	Field('zip_code', 'string'),
	Field('notes', 'string'),
	Field('pic', 'blob'),
	Field('crew', 'integer', default=None, ondelete='SET NULL'),
	Field('grade', 'integer'),
	Field('leader', 'boolean', default=False))

db.define_table('teacher',
	Field('teacher_id', 'integer', notnull=True, unique=True),
	Field('teacher_name', 'string', notnull=True))

db.define_table('course',
	Field('course_id', 'integer', notnull=True, unique=True),
	Field('code', 'string', notnull=True),
	Field('title', 'string', notnull=True),
	Field('period', 'integer', notnull=True),
	Field('teacher_id', 'reference teacher', notnull=True))

db.define_table('course_rec',
	Field('course_id', 'reference course', notnull=True),
	Field('student_id', 'reference person', notnull=True))

db.define_table('groups',
	Field('name', 'string', notnull=True, required=True, unique=True),
	Field('description', 'string'))

db.define_table('group_rec',
	Field('group_id', 'reference groups', notnull=True, required=True),
	Field('person_id', 'reference person', notnull=True, required=True))

db.define_table('events',
	Field('title', 'string'),
	Field('notes', 'string'),
	Field('start_time', 'integer'),
	Field('end_time', 'integer'),
	Field('allDay', 'boolean', default=False),
	Field('recurring', 'boolean', default=False),
	Field('end_recur', 'integer'))

db.define_table('attendance',
	Field('event_id', 'reference events', notnull=True, required=True),
	Field('person_id', 'reference person', notnull=True, required=True),
	Field('present', 'boolean', default=True))

db.define_table('module_names',
	Field('name', 'string', notnull=True, unique=True),
	Field('label', 'string', notnull=True))

db.define_table('file',
	Field('name', 'string', notnull=True),
	Field('file', 'upload', notnull=True))

class_list = [None, 'Pre-Algebra', 'Algebra I', 'Algebra II', 
	'Geometry', 'Pre-Calculus', 'Geography', 'World History',
	'U.S. History', "Gov't/Econ", 'English/Writing', 'Biology',
	'Chemistry', 'Physics', 'AVID', 'French', 'German', 'Spanish',
	'Sign Language']

db.define_table('study_buddy',
	Field('person_id', db.person, notnull=True, 
		required=True, label="Student", 
		requires=IS_IN_SET([
			(p.id, p.last_name + ", " + p.first_name) 
			for p in db(db.person.leader==True).select(db.person.ALL, orderby=[db.person.last_name, db.person.first_name])]
		)),
	Field('days', 'string', notnull=True, required=True, requires=IS_IN_SET(["Tuesday", "Thursday", "Both"])),
	Field('semester', 'string', notnull=True, required=True, requires=IS_IN_SET(["Fall", "Spring", "Both"])),
	Field('lunch', 'string', notnull=True, required=True, requires=IS_IN_SET(["Yes", "No"]), label="Mon/Wed/Fri Lunch?"),
	Field('sport_season', 'list:string', notnull=True, required=True, default=None, requires=IS_IN_SET([None, "Fall", "Winter", "Spring", "Summer"], multiple=False)),
	Field('academic_subject1', 'string', notnull=True, required=True, default=None, requires=IS_IN_SET(class_list, multiple=False)),
	Field('academic_subject2', 'string', notnull=True, required=True, default=None, requires=IS_IN_SET(class_list, multiple=False)),
	Field('academic_subject3', 'string', notnull=True, required=True, default=None, requires=IS_IN_SET(class_list, multiple=False)),
	Field('nickname', 'string', notnull=True, required=True),
	Field('grad_year', 'integer', notnull=True, required=True),
	Field('second_language', 'string'))

db.define_table('score',
	Field('crew_id', 'reference crew', notnull=True),
	Field('score', 'string', notnull=True))

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)