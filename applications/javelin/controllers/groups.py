@auth.requires_login()
def index():
	return dict()

@auth.requires_login()
def create_group():
	return dict()

@auth.requires_login()
def delete_group():
	return dict()