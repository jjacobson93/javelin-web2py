# -*- coding: utf-8 -*-
"""
	Javelin Web2Py Events Controller
"""

# metadata
__author__ = "Jeremy Jacobson"
__copyright__ = "(c) 2013, Jacobson and Varni, LLC"
__date__ = "7/22/2013"
__email__ = "jjacobson93@gmail.com"
__status__ = "Development"
__data__ = {'name' : 'events', 'label' : 'Events', 'description' : 'Manage and create events', 
	'icon' : 'calendar', 'u-icon' : u'\uf073', 'color':'red', 'required' : True}

from applications.javelin.ctr_data import ctr_enabled, get_ctr_data
from gluon.contrib import simplejson as json
from gluon.tools import Service
service = Service(globals())

@auth.requires_login()
@auth.requires_membership('standard')
def index():
	"""Loads the index page for the 'Events' controller

	:returns: a dictionary to pass to the view with the list of modules_enabled and the active module ('events')
	"""
	return dict(ctr_enabled=ctr_enabled, ctr_data=get_ctr_data(), active_module='events')

@auth.requires_login()
@auth.requires_membership('standard')
@service.json
def data(start=None, end=None, _=None):
	"""Loads the event data

	:param start: the start time
	:param end: the end time
	:returns: a list of events between the start and end times
	"""
	if (start is not None) and (end is not None):
		start = int(start)
		end = int(end)

		total_weeks = (end - start)/604800

		event_list = db(db.events.recurring==False,
			( (db.events.start_time >= start) & (db.events.start_time < end) ) |
			( (db.events.end_time >= start) &  (db.events.end_time < end) ) |
			( (db.events.start_time <= start) & (db.events.end_time >= end) ) ).select(db.events.ALL).as_list()


		recur_events = db(db.events.recurring==True,
			( (db.events.start_time < end) & 
				( (db.events.end_recur==None) | 
					( (db.events.end_recur!=None) & (db.events.end_recur > start) ) ) ) ).select(db.events.ALL).as_list()

		for e in recur_events:
			if e['end_recur']:
				if e['start_time'] > start: a = start
				else: a = e['start_time']
				if e['end_recur'] > end: b = end
				else: b = e['end_recur']

				weeks = (b - a)/604800
			else:
				weeks = (end - e['start_time'])/604800
				if weeks > total_weeks: weeks = total_weeks

			for i in range(weeks):
				event_list.append(e)
				e = e.copy()
				e['start_time'] += 604800
				e['end_time'] += 604800

		event_list = [dict(('start', v) if k=='start_time' else (('end', v) if k=='end_time' else (k,v)) for k, v in d.items()) for d in event_list]
	else:
		event_list = db().select(db.events.ALL, orderby=db.events.start_time).as_list()

	return event_list

@auth.requires_login()
@auth.requires_membership('standard')
@service.json
def add_event(title, start, end, notes=None, allDay=False, recurring=False, end_recur=None):
	"""Adds an event

	:param title: the title for the event
	:param start: start time for the event
	:param end: end time for the event
	:param notes: notes for the event
	:returns: a dictionary with a response of success or failure
	"""
	select = db(db.events.title==title).select().as_list()
	if len(select) == 0:
		response = db.events.insert(title=title, start_time=start, end_time=end, allDay=allDay, notes=notes, recurring=recurring, end_recur=end_recur)
		return dict(response=response)
	else:
		return dict(exists=True)

@auth.requires_login()
@auth.requires_membership('standard')
@service.json
def delete_event(id):
	"""Deletes an event

	:param id: the id of the event
	:returns: a dictionary with a response of success or failure
	"""
	response = db(db.events.id==id).delete()
	return dict(response=response)

@auth.requires_login()
@auth.requires_membership('standard')
def call():
	"""Call function used when calling a function from an HTTP request"""
	return service()