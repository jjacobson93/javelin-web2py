# -*- coding: utf-8 -*-
"""
	Javelin Web2Py Admin Module
"""

# metadata
__author__ = "Jeremy Jacobson"
__copyright__ = "(c) 2013, Jacobson and Varni, LLC"
__date__ = "7/12/2013"
__email__ = "jjacobson93@gmail.com"
__data__ = {'name' : 'jadmin', 'label' : 'Admin', 'description' : 'Only accessible to admins', 
	'icon' : 'briefcase', 'u-icon' : u'\uf0b1', 'required' : True}

from globals import current

def update_names(names):
	db = current.javelin.db

	response = []
	for name in names:
		r = db.module_names.update_or_insert(name=name['name'], label=name['value'])
		response.append(r)

	return response

def import_from_csv(csv_file, contains_ids):
	db = current.javelin.db

	import logging
	logger = logging.getLogger('web2py.app.javelin')

	response = list()

	lines = csv_file.rstrip().splitlines()

	if len(lines) > 0:
		columns = lines.pop(0).split(',')

		for i in range(len(columns)):
			columns[i] = '_'.join(columns[i].lower().split())

		for line in lines:
			record = dict()
			line = line.split(',')
			for i in range(len(line)):
				record[columns[i]] = line[i]

			record = dict((k,v) for k,v in record.items() if k in db.person.fields)
			response.append(db.person.update_or_insert(db.person.id==record['id'], **record))

	return dict(response=response)