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