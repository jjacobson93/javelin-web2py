ctr_available = {
	'people': 		{'name' : 'people', 'label' : 'People', 'description' : 'Keep track of people and edit their data', 
					 'icon' : 'user', 'u-icon' : u'\uf007', 'color': 'blue', 'required' : True},
	'groups': 		{'name' : 'groups', 'label' : 'Groups', 'description' : 'Create groups and add people to them', 
					 'icon' : 'book', 'u-icon' : u'\uf02d', 'color': 'green', 'required' : True},
	'events': 		{'name' : 'events', 'label' : 'Events', 'description' : 'Manage and create events', 
					 'icon' : 'calendar', 'u-icon' : u'\uf073', 'color':'red', 'required' : True},
	'jadmin': 		{'name' : 'jadmin', 'label' : 'Admin', 'description' : 'Only accessible to admins', 
					 'icon' : 'briefcase', 'u-icon' : u'\uf0b1', 'color':'orange', 'required' : True},
	'messages': 	{'name' : 'messages', 'label' : 'Messages', 'description' : 'Send Email and SMS messages to people', 
					 'icon' : 'comment', 'u-icon' : u'\uf075', 'color': 'light-blue', 'required' : True},
	'orientation':	{'name' : 'orientation', 'label' : 'Orientation', 'description' : 'The interface for Crusher Crew Orientation', 
					 'icon' : 'compass', 'u-icon' : u'\uf14e', 'color': 'yellow', 'required' : True},
	'peersupport':	{'name' : 'peersupport', 'label' : 'Peer Support', 'description' : 'Issue tracking system for Peer Support', 
					 'icon' : 'heart', 'u-icon' : u'\uf004', 'color': 'pink', 'required' : True},
}

__all__ = ['people', 'groups', 'events', 'messages', 'orientation', 'peersupport', 'jadmin']
ctr_enabled = [ctr_available[m] for m in __all__]

def get_ctr_data():
	"""Get data about modules"""
	from globals import current
	db = current.javelin.db

	from collections import OrderedDict as odict
	rows = db().select(db.module_names.ALL).as_list()

	labels = {}
	if rows:
		for r in rows:
			labels[r['name']] = r['label']

	ctr = odict()
	for data in ctr_enabled:
		data = data.copy()
		name = data['name']
		if name in labels:
			data['custom'] = labels[name]
		if 'custom' in data:
			label = data['custom']
		else:
			label = data['label']
		ctr_labels = {}
		ctr_labels['cap'] = label
		ctr_labels['lower'] = label.lower()
		if label[-1] == 's':
			ctr_labels['sing'] = label[:-1]
		data['labels'] = ctr_labels
		ctr[name] = data
		del data
	
	return ctr