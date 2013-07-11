# -*- coding: utf-8 -*-
"""
	Javelin Web2Py Modules
"""

# metadata
__author__ = "Jeremy Jacobson"
__copyright__ = "(c) 2013, Jacobson and Varni, LLC"
__date__ = "7/5/2013"
__email__ = "jjacobson93@gmail.com"

# from applications.javelin.models.sqladb import Table, metadata

__all__ = ['people', 'groups']
modules_enabled = list()
modules_data = None

def get_module_data():
	"""Get data about modules"""
	# module_names = Table('module_names', metadata, autoload=True)

	from collections import OrderedDict as odict
	# try:
	# 	rows = module_names.select().execute().fetchall()
	# except:
	# 	return None

	labels = {}
	# for r in rows:
	# 	labels[r['name']] = r['label']

	mods = odict()
	for mod in modules_enabled:
		data = getattr(mod, '__data__').copy()
		name = data['name']
		if name in labels:
			data['custom'] = labels[name]
		if 'custom' in data:
			label = data['custom']
		else:
			label = data['label']
		mod_labels = {}
		mod_labels['cap'] = label
		mod_labels['lower'] = label.lower()
		if label[-1] == 's':
			mod_labels['sing'] = label[:-1]
		data['labels'] = mod_labels
		mods[name] = data
		del mod
	# del module_names
	
	return mods

def init_modules():
	global modules_enabled, modules_data
	for m in __all__:
		modules_enabled.append(__import__('applications.javelin.modules.%s' % m, globals(), locals(), [m]))

	modules_data = get_module_data()

init_modules()