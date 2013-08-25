# from applications.javelin.ctr_data import data
# __all__ = ['people', 'groups', 'events', 'messages', 'orientation', 'scores', 'peersupport', 'jadmin']
# ctr_enabled = [data[m] for m in __all__]
# del data

# def get_ctr_data():
# 	"""Get data about modules"""
# 	from globals import current
# 	db = current.javelin.db

# 	from collections import OrderedDict as odict
# 	rows = db().select(db.module_names.ALL).as_list()

# 	labels = {}
# 	if rows:
# 		for r in rows:
# 			labels[r['name']] = r['label']

# 	ctr = odict()
# 	for data in ctr_enabled:
# 		data = data.copy()
# 		name = data['name']
# 		if name in labels:
# 			data['custom'] = labels[name]
# 		if 'custom' in data:
# 			label = data['custom']
# 		else:
# 			label = data['label']
# 		ctr_labels = {}
# 		ctr_labels['cap'] = label
# 		ctr_labels['lower'] = label.lower()
# 		if label[-1] == 's':
# 			ctr_labels['sing'] = label[:-1]
# 		data['labels'] = ctr_labels
# 		ctr[name] = data
# 		del data
	
# 	return ctr

# def init_ctr():
# 	global ctr_enabled


# 	if not ctr_enabled:
# 		# ctr_enabled = [data[m] for m in __all__]
# 		# for m in __all__:
# 		# 	ctr_enabled.append(data[m])

# init_ctr()