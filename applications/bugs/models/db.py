# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

import logging
logger = logging.getLogger('web2py.app.bugs')
logger.setLevel(logging.DEBUG)
from conf import *

from gluon.custom_import import track_changes
track_changes(True)

if not request.env.web2py_runtime_gae:
	## if NOT running on Google App Engine use SQLite or other DB
	# db = DAL('sqlite://storage.sqlite',pool_size=1,check_reserved=['all'],migrate=False)
	db = DAL(DB_URI)
	session.connect(request, response, db=db, masterapp='javelin')
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
auth.define_tables(username=True, signature=False, migrate=False)

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

user_agent = request.user_agent()

db.define_table('ticket',
	Field('description', 'string', notnull=True, required=True),
	Field('steps', 'text', notnull=True, required=True, default="", label='Steps to reproduce'),
	Field('type', 'string', notnull=True, required=True, requires=IS_IN_SET(["enhancement", "minor", "major", "critical"])),
	Field('created_on', 'datetime', notnull=True, default=request.now, required=True, writable=False),
	Field('user_id', 'reference auth_user', default=auth.user.id if auth.user else None, notnull=True, writable=False, readable=False),
	Field('client_ip', 'string', default=request.client, notnull=True, required=True, writable=False, readable=False),
	Field('user_agent', 'string', notnull=True, required=True, default=str(user_agent.browser.name + " (" + user_agent.browser.version + ")"), writable=False, readable=False),
	Field('os', 'string', notnull=True, required=True, default=str(user_agent.flavor.name + " " + user_agent.flavor.version), writable=False, readable=False),
	Field('approved', 'boolean', notnull=True, default=False, writable=False, readable=False),
	Field('fixed', 'boolean', notnull=True, default=False, writable=False, readable=False), migrate=False)