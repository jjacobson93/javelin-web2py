def formstyle_javelin(form, fields):
	parent = DIV()
	for id, label, controls, help in fields:
		# submit unflag by default
		_submit = False
		if isinstance(controls, INPUT):
			controls.add_class('form-control')

			if controls['_type'] == 'submit':
				# flag submit button
				_submit = True
				controls['_class'] = 'btn blue btn-lg btn-block'
			if controls['_type'] == 'button':
				controls['_class'] = 'btn btn-default'
			elif controls['_type'] == 'file':
				controls['_class'] = 'input-file'
			elif controls['_type'] == 'text':
				controls['_placeholder'] = label[0]
				controls['_class'] = 'form-control'
			elif controls['_type'] == 'password':
				controls['_placeholder'] = label[0]
				controls['_class'] = 'form-control'
			elif controls['_type'] == 'checkbox':
				controls['_class'] = 'checkbox'

		# # For password fields, which are wrapped in a CAT object.
		# if isinstance(controls, CAT) and isinstance(controls[0], INPUT):
		#     controls = INPUT(_placeholder='Test', _class='form-control')

		if isinstance(controls, SELECT):
			controls.add_class('form-control')

		if isinstance(controls, TEXTAREA):
			controls.add_class('form-control')

		if isinstance(label, LABEL):
			label['_class'] = 'control-label'


		# if _submit:
		#     # submit button has unwrapped label and controls, different class
		#     parent.append(DIV(label, DIV(controls,_class="col-lg-4 col-lg-offset-2"), _class='form-group', _id=id))
		#     # unflag submit (possible side effect)
		#     _submit = False
		# else:
		#     # unwrapped label
		parent.append(DIV(controls, _class='form-group', _id=id))

	return parent

auth.settings.formstyle = formstyle_javelin