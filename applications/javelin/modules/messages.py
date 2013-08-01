# -*- coding: utf-8 -*-
"""
	Javelin Web2Py Messages Module
"""

# metadata
__author__ = "Jeremy Jacobson"
__copyright__ = "(c) 2013, Jacobson and Varni, LLC"
__date__ = "7/28/2013"
__email__ = "jjacobson93@gmail.com"
__data__ = {'name' : 'messages', 'label' : 'Messages', 'description' : 'Send Email and SMS messages to people', 
	'icon' : 'comment', 'u-icon' : u'\uf075', 'required' : True}

from globals import current
from gluon.contrib.sms_utils import sms_email

class Providers(object):
	ATT = 'AT&T'
	VERIZON = 'Verizon Wireless (vtext)'
	SPRINT = 'Sprint PCS'
	METRO_PCS = 'Metro PCS'
	TMOBILE = 'T-Mobile USA (tmail)'

	@staticmethod
	def contains(e):
		if e.lower() in ('at&t', 'at & t', 'verizon',
			'metro pcs', 'metro-pcs', 'sprint pcs', 'sprint', 
			't-mobile', 't mobile'):
			return True
		else:
			return False

	@staticmethod
	def get(e):
		if e.lower() in ('at&t', 'at & t'):
			return Providers.ATT
		elif e.lower() in ('verizon'):
			return Providers.VERIZON
		elif e.lower() in ('metro pcs', 'metro-pcs'):
			return Providers.METRO_PCS
		elif e.lower() in ('sprint pcs', 'sprint'):
			return Providers.SPRINT
		elif e.lower() in ('t-mobile', 't mobile'):
			return Providers.TMOBILE
		else:
			return None



def send_sms(message, to):
	db = current.javelin.db
	mail = current.javelin.mail

	bcc = list()
	if to == 'all_leaders':
		people = db((db.person.grade != 9) & (db.person.leader==True)).select(
			db.person.id, db.person.student_id, db.person.cell_phone, db.person.cell_provider)

		for person in people:
			if person.cell_phone and person.cell_provider and Providers.contains(person.cell_provider):
				bcc.append(sms_email(person.cell_phone, Providers.get(person.cell_provider)))
			elif person.email:
				bcc.append(person.email)

	else:
		person = db(db.person.id==to).select().first()

		if person.cell_phone and person.cell_provider and Providers.contains(person.cell_provider):
			bcc.append(sms_email(person.cell_phone, Providers.get(person.cell_provider)))
		elif person.email:
			bcc.append(person.email)

	if len(bcc) < 100:
		mail.send(to=mail.settings.sender, bcc=bcc, subject='', message=message)
	else:
		small_lists = list()
		curr = list()
		count = 0
		while len(bcc) > 0:
			if count < 50:
				curr.append(bcc.pop(0))
			else:
				small_lists.append(curr)
				curr = list()
				curr.append(bcc.pop(0))
				count = 0
			count += 1
		for l in small_lists:
			mail.send(to=mail.settings.sender, bcc=l, subject='', message=message)

	return dict(response='Sending messages')