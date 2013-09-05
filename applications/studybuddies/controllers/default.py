# -*- coding: utf-8 -*-
"""
	Javelin SB Web2Py Default Controller
"""

from gluon.storage import Storage
import datetime

@auth.requires_login()
def index():
	"""
	example action using the internationalization operator T and flash
	rendered by views/default/index.html or views/generic.html

	if you need a simple wiki simple replace the two lines below with:
	return auth.wiki()
	"""
	currdate = request.now.strftime('%Y-%m-%d-%H-%M-%S') #this is UTC time
	return dict(currdate=currdate)

@auth.requires_login()
def sections():
	start = request.vars.get('start', None)
	end = request.vars.get('end', None)
	if start and end:
		sections = dict(('_'.join(s.title.lower().split()), s.id) for s in db().select(db.sb_section.id, db.sb_section.title))
		return dict(sections=sections, counts=counts(start, end))
	else:
		return dict(sections=[], counts=dict())
		

@auth.requires_login()
def table():
	start = request.vars.get('start', None)
	end = request.vars.get('end', None)

	section = request.vars['section_id']
	if start and end:
		start = datetime.datetime.strptime(start, '%Y-%m-%d-%H-%M-%S')
		end = datetime.datetime.strptime(end, '%Y-%m-%d-%H-%M-%S')
		
		students = db(((db.sb_att.in_time >= start) & (db.sb_att.in_time < end)) |
			((db.sb_att.out_time >= start) & (db.sb_att.out_time < end)) ).select(
				db.person.ALL, db.sb_att.ALL, 
				join=db.sb_att.on((db.person.id==db.sb_att.person_id) & (db.sb_att.sb_section_id==section)),
				orderby=[~db.sb_att.in_time, ~db.sb_att.out_time])

		return dict(students=students)
	else:
		return dict(students=list())

@auth.requires_login()
@service.json
def checkin(person_id, section_id=None):
	student = db((db.person.student_id==person_id) | 
		(db.person.id==person_id)).select().first()
	result = None
	error = None

	if student and section_id:
		person_id = student.id

		check = db((db.sb_att.is_out==False) & 
			(db.sb_att.person_id==person_id) &
			(db.sb_att.sb_section_id==section_id)).select().first()

		if not check:
			checktwo = db((db.sb_att.person_id==person_id) & 
				(db.sb_att.is_out==False)).select()
			if checktwo:
				for c in checktwo:
					update = db((db.sb_att.person_id==person_id) & 
						(db.sb_att.id==c.id)).update(studyhour=calc_hour(c.in_time), is_out=True) # if not checked out of other section, check out
			result = db.sb_att.insert(person_id=person_id, sb_section_id=section_id)
		else:
			result = 'Already exists'
			error = True

		return dict(response=result, error=error)

	elif student and not section_id:
		person_id = student.id
		
		section = db(db.sb_section.title=="Other").select(db.sb_section.id).first()
		if section:
			check = db((db.sb_att.is_out==False) & 
				(db.sb_att.person_id==person_id) &
				(db.sb_att.sb_section_id==section.id)).select().first()

			if not check:
				checktwo = db((db.sb_att.person_id==person_id) & 
				(db.sb_att.is_out==False)).select()
				if checktwo:
					for c in checktwo:
						update = db((db.sb_att.person_id==person_id) & 
							(db.sb_att.id==c.id)).update(studyhour=calc_hour(c.in_time), is_out=True) # if not checked out of other section, check out
				result = db.sb_att.insert(person_id=person_id, sb_section_id=section.id)
			else:
				result = 'Already exists'
				error = True

			return dict(response=result, error=error)
	
	
	result = "No person exists with ID"
	error = True
	return dict(response=result, error=error)

@auth.requires_login()
@service.json
def checkout(person_id):
	student = db((db.person.student_id==person_id) | 
		(db.person.id==person_id)).select().first()
	result = None
	error = None

	if student:
		person_id = student.id

		check = db((db.sb_att.is_out==False) &
					(db.sb_att.person_id==person_id)).select()
		if check:
			for c in check:
				db(db.sb_att.id==c.id).update(studyhour=calc_hour(c.in_time), is_out=True)
		else:
			result = 'Does not exist'
			error = True
	else:
		result = "No person exists with ID"
		error = True

	return dict(response=result, error=error)

@auth.requires_login()
def checkoutall():
	currdate = request.now.strftime('%Y-%m-%d-%H-%M-%S') #this is UTC time
	return dict(currdate=currdate)

@auth.requires_login()
def checkout_table():
	start = request.vars.get('start', None)
	end = request.vars.get('end', None)

	if start and end:
		start = datetime.datetime.strptime(start, '%Y-%m-%d-%H-%M-%S')
		end = datetime.datetime.strptime(end, '%Y-%m-%d-%H-%M-%S')

		records = db(((db.sb_att.in_time >= start) & 
			(db.sb_att.in_time < end)) &
			(db.sb_att.is_out==True)).select(
				db.person.ALL, db.sb_att.ALL, db.sb_section.ALL,
				join=[db.sb_att.on(db.person.id==db.sb_att.person_id),
					db.sb_section.on(db.sb_section.id==db.sb_att.sb_section_id)],
				orderby=db.person.id|db.person.last_name|db.person.first_name,
				distinct=db.person.id)

		def recordsfor(id):
			return db(((db.sb_att.in_time >= start) & 
				(db.sb_att.in_time < end)) &
			(db.sb_att.is_out==True)).select(
				db.person.ALL, db.sb_att.ALL, db.sb_section.ALL,
				join=[db.sb_att.on((db.person.id==db.sb_att.person_id) & (db.person.id==id)),
					db.sb_section.on(db.sb_section.id==db.sb_att.sb_section_id)],
				orderby=[db.person.last_name, db.person.first_name])

		students = list()
		for p in records:
			s = Storage(subjects=[],totalhours=[], in_time=None, out_time=None, **dict((c,v) for c, v in p.items()))
			for r in recordsfor(p.person.id):
				s.subjects.append(str(r.sb_section.title))
				s.totalhours.append(r.sb_att.studyhour)
				if not s.in_time or (r.sb_att.in_time and r.sb_att.in_time < s.in_time):
					s.in_time = r.sb_att.in_time

				if not s.out_time or (r.sb_att.out_time and r.sb_att.out_time > s.out_time):
					s.out_time = r.sb_att.out_time

			s.subjects = ', '.join(s.subjects)
			s.totaltime = s.out_time - s.in_time

			students.append(s)

		students = sorted(students, key=lambda s: s.person.last_name)

		return dict(students=students)

	return dict(students=list())

@auth.requires_login()
@service.json
def checkout_any(person_id):
	student = db((db.person.student_id==person_id) | 
		(db.person.person_id==person_id)).select().first()
	result = None
	error = None

	if student:
		person_id = student.student_id

		check = db((db.sb_att.is_out==False) & 
			(db.sb_att.person_id==person_id)).select().first()
		
		if check:
			result = db(db.sb_att.id==check.id).update(studyhour=calc_hour(check.in_time), is_out=True)
	else:
		result = "No person exists with ID"
		error = True

	return dict(response=result, error=error)

@auth.requires_login()
@service.json
def counts(start, end):
	if start and end:
		start = datetime.datetime.strptime(start, '%Y-%m-%d-%H-%M-%S')
		end = datetime.datetime.strptime(end, '%Y-%m-%d-%H-%M-%S')

		sections = db().select(db.sb_section.ALL)
		counts = dict(('_'.join(s.title.lower().split()), 
			db( (((db.sb_att.in_time >= start) & (db.sb_att.in_time < end)) |
				((db.sb_att.out_time >= start) & (db.sb_att.out_time < end))) & 
				(db.sb_att.sb_section_id==s.id) & 
				(db.sb_att.is_out==False)).count()) for s in sections)
		return counts
	else:
		return dict()

@auth.requires_login()
@service.json
def make_void(record_ids):
	record_ids = json.loads(record_ids)
	for r in record_ids:
		db(db.sb_att.id==r).update(void=True)

	return dict(success=True)

@auth.requires_login()
@service.json
def print_receipt(data):
	data = json.loads(data)

	ESC = '\x1B'
	LF = '\x0A'
	RESET = ESC + '\x40'
	L_ALIGN = ESC + '\x1D\x61\x30'
	C_ALIGN = ESC + '\x1D\x61\x31'
	CUT = '\x1B\x64\x33'

	person = db(db.person.id==data['id']).select(db.person.ALL).first()
	receipt = ''
	receipt = RESET

	# Add Image
	# receipt += ESC + '*rR' # Init raster mode
	# receipt += ESC + '*rA' # Enter raster mode
	# receipt += ESC + '*rC' # Clear raster data
	# receipt += ESC + '*rml' # Set left margin
	# receipt += 'b\x30\x01'
	# receipt += '\x00\x00\x1F\xF8\x3F\xFC\x77\xEE\xF8\x1F\xF8\x1F\xF8\x1F\x0F\xF0\x1F\xF8\x1F\xF8\x3E\x7C\x38\x1C\x79\x9E\x73\xCE\x73\xCE\xF9\x9F\xF8\x1F\xFE\x7F\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00'
	# receipt += ESC + '\x0C\x00'
	# receipt += ESC + '*rB'

	# receipt += ESC + "\x4b\x02\x00"
	# receipt += '\x1F\xF8'
	# receipt += '\x64\x64\x64\x64\x64\x64\x64'
	# receipt += "\n\x01\xfc\xc1\x1f\x07\xff\xe3\x1f\x07\xff" +\
	# 	"\xf3\x1f\x0f\xff\xfb\n\x1f\x0f\xff\xfb\x1f\x1f\xff" +\
	# 	"\xfb\x1f\x1f\xfe\xfd\x1f\x1f\xfe\n\xfd\x1b\x3f\xfe" +\
	# 	"\xbe\x17\x3f\xfc\xde\x07\x7f\x78\xde\x07\x7f\n\x78" +\
	# 	"\xb0\x17\x3f\x78\xf1\x13\x1f\xb8\xf3\x1b\x8f\xb0\xf3" +\
	# 	"\x19\n\x87\xf1\xf7\x1c\xc7\xd1\xf7\x1f\xc3\xe1\xff" +\
	# 	"\x1f\xc3\xe3\x3f\n\x10\xe3\xe3\xff\x1f\xe3\xf7\xff" +\
	# 	"\x1f\xe3\xf7\xff\x1f\xc3\xff\n\xff\x1f\xc3\xff\xff" +\
	# 	"\x1f\xc3\xff\xff\x1f\xc7\xff\xff\x1f\x87\n\xff\xff" +\
	# 	"\x1f\x8f\xff\xff\x1f\x0f\xff\xfb\x1f\x3f\xfe\xfd" +\
	# 	"\x1f\n\x7f\x00\xfe\x1f\xff\xc7\xff\x1f\n"

	# receipt += ESC + '\x4b\x1e\x00'
	# receipt += '\x01\x1E\x3E\x5F\x1F\x5E\x1E\x3F\x2F\x3E\x3E\x02\x02\x3E\x3E\x2F\x2F\x3E\x2E\x2E\x3E\x2E\x2E\x3E\x2F\x2F\x3E\x3E\x02\x02'

	# receipt += '\x1b\x2a\x72\x52'
	# receipt += '\x1b\x2a\x72\x41'
	# receipt += '\x1b\x2a\x72\x43'
	# receipt += '\x1b\x62\x02\x00\x00\x00'
	# receipt += '\x1b\x62\x02\x00\x1F\xF8'
	# receipt += '\x1b\x62\x02\x00\x3F\xFC'
	# receipt += '\x1b\x62\x02\x00\x77\xEE'
	# receipt += '\x1b\x62\x02\x00\xF8\x1F'
	# receipt += '\x1b\x62\x02\x00\xF8\x1F'
	# receipt += '\x1b\x62\x02\x00\xF8\x1F'
	# receipt += '\x1b\x62\x02\x00\x0F\xF0'
	# receipt += '\x1b\x62\x02\x00\x1F\xF8'
	# receipt += '\x1b\x62\x02\x00\x1F\xF8'
	# receipt += '\x1b\x62\x02\x00\x3E\x7C'
	# receipt += '\x1b\x62\x02\x00\x38\x1C'
	# receipt += '\x1b\x62\x02\x00\x79\x9E'
	# receipt += '\x1b\x62\x02\x00\x73\xCE'
	# receipt += '\x1b\x62\x02\x00\x73\xCE'
	# receipt += '\x1b\x62\x02\x00\xF9\x9F'
	# receipt += '\x1b\x62\x02\x00\xF8\x1F'
	# receipt += '\x1b\x62\x02\x00\xFE\x7F'
	# receipt += '\x1b\x62\x02\x00\xFF\xFF'
	# receipt += '\x1b\x62\x02\x00\xFF\xFF'
	# receipt += '\x1b\x0C\x00'
	# receipt += '\x1b\x2a\x72\x42'

	# 01111111 11110000 11111111 0000000
	# 00011111 11000000 00111110 0000000
	# 00001111 10000000 00011000 0000000
	# 00001111 10000000 00011000 0000000
	# 00000111 10000000

	# imageData = ['\x7f', '\xf0', '\xff', '\x00', '\x1f', '\xc0', '>',
	# '\x00', '\x0f', '\x80', '\x18', '\x00', '\x0f', '\x80', '\x18',
	# '\x00', '\x07', '\x80', '8', '\x00', '\x07', '\xc0', '0', '\x00',
	# '\x03', '\xc0', '0', '\xe0', '\x03', '\xe0', 'a', '\xf8', '\x03',
	# '\xe0', 'c', '\x1c', '\x01', '\xe0', 'C', '\x0c', '\x01', '\xff',
	# '\xcb', '\x0c', '\x01', '\xf1', '\xfb', '\x9c', '\x03', '\xf1',
	# '\xf9', '\xdc', '\x07', '\xf9', '\xb8', '8', '\x0f', '{', '\x18',
	# '0', '\x0f', '{', '\x18', '`', '\x1f', '\x7f', '\x18', '\xc4',
	# '\x1e', '>', '\t', '\xbc', '\x1e', '>', '\x03', '\xfc', '>',
	# '\x1c', '\x03', '\xf8', '>', '\x1c', '\x00', '\x00', '>', '\x18',
	# '\x00', '\x00', '>', '\x00', '\x00', '\x00', '\x1e', '\x00',
	# '\x00', '\x00', '\x1e', '\x00', '\x00', '\x00', '\x1f', '\x00',
	# '\x0c', '\x00', '\x0f', '\x00', '\x08', '\x00', '\x0f', '\x80',
	# '\x18', '\x00', '\x07', '\xc0', '8', '\x00', '\x03', '\xe0', 'p',
	# '\x00', '\x01', '\xff', '\xe0', '\x00', '\x00', '?', '\x80',
	# '\x00']

	# width = 32
	# height = 32
	# bitmapBytePerRow = width/8
	# bytesPerRow = 3 + bitmapBytePerRow;
	# receipt += ESC + '\x2A\x72\x52'
	# receipt += ESC + '\x2A\x72\x41'
	# receipt += ESC + '\x2A\x72\x43'
	# x = 0
	# while x < len(imageData):
	# 	rasterCommandForRow = ''.join([imageData[i] for i in range(x, x+4)])
	# 	x += 4
	# 	receipt += rasterCommandForRow

	# receipt += ESC + '\x1b\x0C\x00'
	# receipt += ESC + '\x2A\x72\x42'


				# if out:
			# 	lastDot = nextOut

	# byteOffset = 0
	# for y in range(0, height):
	# 	rasterCommandForRow = '\x6B'
	# 	rasterCommandForRow += chr(int((width*height)%256))
	# 	rasterCommandForRow += chr(int((width*height)/256))
	# 	mask_int = 128
	# 	mask = chr(mask_int)
	# 	out = chr(0)
	# 	for x in range(0, width):
	# 		if byteOffset < len(imageData) and imageData[byteOffset]:
	# 			out += mask
	# 		byteOffset += 1
	# 		mask_int >>= 1
	# 		if 0 == mask_int:
	# 			mask_int = 128
	# 			mask = chr(mask_int)
	# 			rasterCommandForRow += out
	# 			out = chr(0)
	# 	if ('\x80' != mask) and (0 != out):
	# 		rasterCommandForRow += out
		# receipt += rasterCommandForRow

	# sdata = [ESC + '\x4b\x1e\x00', 'K\x00\x04\xe0', '\x00\x00\x00K', '\x00\x04\x0f\xff', '\x00\x00K\x00', '\x04\x00\xff\xff', '\xffK\x00\x04', '\xff\x80\x00\x03', 'K\x00\x04\xff', '\xff\xfc\x00K', '\x00\x04\x07\xff', '\xff\xffK\x00', '\x04\xff\xf0\x00', '\x1fK\x00\x04', '\xff\xff\xff\x81', 'K\x00\x04\xff', '\xff\xff\xffK', '\x00\x04\xff\xf0', '\x00\x1fK\x00', '\x04\xff\xff\xff', '\x81K\x00\x04', '\xff\xff\xff\xff', 'K\x00\x04\xff', '\xfe\x00\x1fK', '\x00\x04\xff\xff', '\xff\x81K\x00', '\x04\xff\xff\xff', '\xffK\x00\x04', '\xff\xfe\x00\x03', 'K\x00\x04\xff', '\xff\xfc\x0fK', '\x00\x04\xff\xff', '\xff\xffK\x00', '\x04\xff\xff\xc0', '\x03K\x00\x04', '\xff\xff\xfc\x0f', 'K\x00\x04\xff', '\x00\x7f\xffK', '\x00\x04\xff\xff', '\xc0\x00K\x00', '\x04\x7f\xff\xe0', '\x7fK\x00\x04', '\xf8\x00\x01\xff', 'K\x00\x04\xff', '\xff\xc0\x00K', '\x00\x04\x7f\xff', '\xe0\x7fK\x00', '\x04\xc0\xff\x80', '?K\x00\x04', '\xff\xff\xf8\x00', 'K\x00\x04\x7f', '\xff\xe3\xffK', '\x00\x04\xc0\xff', '\xf0?K\x00', '\x04\xff\xff\xf8', '\x00K\x00\x04', '\x00\x00\x03\xf1', '\x1b\x0c\x00\x1b', '*rC']
	# sdata = [ESC + '\x4b\x1e\x00', 'K\x00\x04\xe0', '\x00\x00\x00K', '\x00\x04\x0f\xff', '\x00\x00K\x00', '\x04\x00\xff\xff', '\xffK\x00\x04', '\xff\x80\x00\x03', 'K\x00\x04\xff', '\xff\xfc\x00K', '\x00\x04\x07\xff', '\xff\xffK\x00', '\x04\xff\xf0\x00', '\x1fK\x00\x04', '\xff\xff\xff\x81', 'K\x00\x04\xff', '\xff\xff\xffK', '\x00\x04\xff\xf0', '\x00\x1fK\x00', '\x04\xff\xff\xff', '\x81K\x00\x04', '\xff\xff\xff\xff', 'K\x00\x04\xff', '\xfe\x00\x1fK', '\x00\x04\xff\xff', '\xff\x81K\x00', '\x04\xff\xff\xff', '\xffK\x00\x04', '\xff\xfe\x00\x03', 'K\x00\x04\xff', '\xff\xfc\x0fK', '\x00\x04\xff\xff', '\xff\xffK\x00', '\x04\xff\xff\xc0', '\x03K\x00\x04', '\xff\xff\xfc\x0f', 'K\x00\x04\xff', '\x00\x7f\xffK', '\x00\x04\xff\xff', '\xc0\x00K\x00', '\x04\x7f\xff\xe0', '\x7fK\x00\x04', '\xf8\x00\x01\xff', 'K\x00\x04\xff', '\xff\xc0\x00K', '\x00\x04\x7f\xff', '\xe0\x7fK\x00', '\x04\xc0\xff\x80', '?K\x00\x04', '\xff\xff\xf8\x00', 'K\x00\x04\x7f', '\xff\xe3\xffK', '\x00\x04\xc0\xff', '\xf0?K\x00', '\x04\xff\xff\xf8', '\x00K\x00\x04', '\x00\x00\x03\xf1', '\x1b\x0c\x00\x1b', '*rC']
	# receipt += ''.join(sdata)


	receipt += '\x1b*rA' # Enter raster mode
	# receipt += '\x1b*rT2\x00' # Top margin '\x1b*rT2\x00'
	receipt += '\x1b*rQ\x01\x00' # Print quality
	receipt += '\x1b*rP0\x00' # Page length
	# receipt += '\x1b*rml0\x00' # Left margin
	# receipt += '\x1b*rmr0\x00' # Right margin
	receipt += '\x1b*rE\x00\x00' # Set EOT mode
	receipt += '\x1b*rF\x00\x00' # Set FF mode
	# receipt += 'b\x04\x00\x7f\xf0\xff\x00'
	# receipt += 'b\x04\x00\x1f\xc0\x3c\x00'
	# receipt += 'b\x04\x00\x0f\x80\x18\x00'
	# receipt += 'b\x04\x00\x0f\x80\x18\x00'
	# receipt += 'b\x04\x00\x07\x80\x38\x00'
	# receipt += 'b\x04\x00\x07\xc0\x30\x00'
	# receipt += 'b\x04\x00\x03\xc0\x30\xe0'
	# receipt += 'b\x04\x00\x03\xe0\x61\xf8'
	# receipt += 'b\x04\x00\x03\xe0\x63\x1c'
	# receipt += 'b\x04\x00\x01\xe0\x43\x0c'
	# receipt += 'b\x04\x00\x01\xff\xcb\x0c'
	# receipt += 'b\x04\x00\x01\xf1\xfb\x9c'
	# receipt += 'b\x04\x00\x03\xf1\xf9\xdc'
	# receipt += 'b\x04\x00\x07\xf9\xb8\x38'
	# receipt += 'b\x04\x00\x0f\x7b\x18\x30'
	# receipt += 'b\x04\x00\x0f\x7b\x18\x60'
	# receipt += 'b\x04\x00\x1f\x7f\x18\xc4'
	# receipt += 'b\x04\x00\x1e\x3e\x09\xbc' # \t
	# receipt += 'b\x04\x00\x1e\x3e\x03\xfc'
	# receipt += 'b\x04\x00\x3e\x1c\x03\xf8'
	# receipt += 'b\x04\x00\x3e\x1c\x00\x00'
	# receipt += 'b\x04\x00\x3e\x18\x00\x00'
	# receipt += 'b\x04\x00\x3e\x00\x00\x00'
	# receipt += 'b\x04\x00\x1e\x00\x00\x00'
	# receipt += 'b\x04\x00\x1e\x00\x00\x00'
	# receipt += 'b\x04\x00\x1f\x00\x0c\x00'
	# receipt += 'b\x04\x00\x0f\x00\x08\x00'
	# receipt += 'b\x04\x00\x0f\x80\x18\x00'
	# receipt += 'b\x04\x00\x07\xc0\x38\x00'
	# receipt += 'b\x04\x00\x03\xe0\x70\x00'
	# receipt += 'b\x04\x00\x01\xff\xe0\x00'
	# receipt += 'b\x04\x00\x00\x3f\x80\x00'
	receipt += '\x62\x04\x00\x7f\x7f\x7f\x7f'
	receipt += '\x1b\x0c\x04'
	receipt += '\x1b*rB' #end command

	# receipt += ''.join(['\x1d', '8', 'L', '\x80', '\x00', '\x00', '\x00', '0', 'p', '0', '\x01', '\x01', '1', ' ', '\x00', ' ', '\x00', '\x7f', '\xf0', '\xff', '\x00', '\x1f', '\xc0', '>', '\x00', '\x0f', '\x80', '\x18', '\x00', '\x0f', '\x80', '\x18', '\x00', '\x07', '\x80', '\x18', '\x00', '\x07', '\xc0', '0', '\x00', '\x03', '\xc0', '0', '\xe0', '\x03', '\xe0', 'a', '\xf8', '\x03', '\xe0', 'c', '\x1c', '\x01', '\xe0', 'C', '\x0c', '\x01', '\xff', '\xcb', '\x0c', '\x01', '\xf0', '\xfb', '\x9c', '\x03', '\xf1', '\xf9', '\xdc', '\x07', '\xf9', '\xb8', '8', '\x0f', '{', '\x18', '0', '\x0f', '{', '\x18', '`', '\x1f', '\x7f', '\x18', '\xc4', '\x1e', '>', '\t', '\xbc', '\x1e', '>', '\x03', '\xfc', '>', '\x1c', '\x03', '\xf8', '>', '\x1c', '\x00', '\x00', '>', '\x18', '\x00', '\x00', '>', '\x00', '\x00', '\x00', '\x1e', '\x00', '\x00', '\x00', '\x1e', '\x00', '\x00', '\x00', '\x1f', '\x00', '\x0c', '\x00', '\x0f', '\x00', '\x08', '\x00', '\x0f', '\x80', '\x18', '\x00', '\x07', '\xc0', '8', '\x00', '\x03', '\xe0', 'p', '\x00', '\x01', '\xff', '\xe0', '\x00', '\x00', '?', '\x80', '\x00'])
	# receipt += ''.join(['\x1d', '8', 'L', '\x80', '\x00', '\x00', '\x00', '0', 'p', '0', '\x01', '\x01', '1', ' ', '\x00', ' ', '\x00', '\x7f', '\x7f', '\x7f', '\x00', '\x1f', '\x7f', '>', '\x00', '\x0f', '\x7f', '\x18', '\x00', '\x0f', '\x7f', '\x18', '\x00', '\x07', '\x7f', '\x18', '\x00', '\x07', '\x7f', '0', '\x00', '\x03', '\x7f', '0', '\x7f', '\x03', '\x7f', 'a', '\x7f', '\x03', '\x7f', 'c', '\x1c', '\x01', '\x7f', 'C', '\x0c', '\x01', '\x7f', '\x7f', '\x0c', '\x01', '\x7f', '\x7f', '\x7f', '\x03', '\x7f', '\x7f', '\x7f', '\x07', '\x7f', '\x7f', '8', '\x0f', '{', '\x18', '0', '\x0f', '{', '\x18', '`', '\x1f', '\x7f', '\x18', '\x7f', '\x1e', '>', '\t', '\x7f', '\x1e', '>', '\x03', '\x7f', '>', '\x1c', '\x03', '\x7f', '>', '\x1c', '\x00', '\x00', '>', '\x18', '\x00', '\x00', '>', '\x00', '\x00', '\x00', '\x1e', '\x00', '\x00', '\x00', '\x1e', '\x00', '\x00', '\x00', '\x1f', '\x00', '\x0c', '\x00', '\x0f', '\x00', '\x08', '\x00', '\x0f', '\x7f', '\x18', '\x00', '\x07', '\x7f', '8', '\x00', '\x03', '\x7f', 'p', '\x00', '\x01', '\x7f', '\x7f', '\x00', '\x00', '?', '\x7f', '\x00'])

	# receipt += '\x1b\x4b\x04\x00'
	# receipt += ''.join(['\x7f', '\x7f', '\x7f', '\x00'])
	# receipt += '\x1b\x4b\x04\x00'
	# receipt += ''.join(['\x1f', '\x7f', '>', '\x00'])
	# receipt += ''.join(['\x7f', '\x7f', '\x7f', '\x00', '\x1f', '\x7f', '>', '\x00', '\x0f', '\x7f', '\x18', '\x00', '\x0f', '\x7f', '\x18', '\x00', '\x07', '\x7f', '\x18', '\x00', '\x07', '\x7f', '0', '\x00', '\x03', '\x7f', '0', '\x7f', '\x03', '\x7f', 'a', '\x7f', '\x03', '\x7f', 'c', '\x1c', '\x01', '\x7f', 'C', '\x0c', '\x01', '\x7f', '\x7f', '\x0c', '\x01', '\x7f', '\x7f', '\x7f', '\x03', '\x7f', '\x7f', '\x7f', '\x07', '\x7f', '\x7f', '8', '\x0f', '{', '\x18', '0', '\x0f', '{', '\x18', '`', '\x1f', '\x7f', '\x18', '\x7f', '\x1e', '>', '\t', '\x7f', '\x1e', '>', '\x03', '\x7f', '>', '\x1c', '\x03', '\x7f', '>', '\x1c', '\x00', '\x00', '>', '\x18', '\x00', '\x00', '>', '\x00', '\x00', '\x00', '\x1e', '\x00', '\x00', '\x00', '\x1e', '\x00', '\x00', '\x00', '\x1f', '\x00', '\x0c', '\x00', '\x0f', '\x00', '\x08', '\x00', '\x0f', '\x7f', '\x18', '\x00', '\x07', '\x7f', '8', '\x00', '\x03', '\x7f', 'p', '\x00', '\x01', '\x7f', '\x7f', '\x00', '\x00', '?', '\x7f', '\x00']))

	# sdatarr = [''.join([chr(int(x + y, 16)) for x, y in zip(i[::2], i[1::2])]) for i in sdata]

	# receipt += '\x1b\x40'
	# receipt += '\x1b\x4c'
	# receipt += '\x0c\x1b\x4A\x78\x1e' # End bitmap

	# Add header
	receipt += C_ALIGN
	receipt += "VINTAGE CRUSHER CREW" + LF
	receipt += "STUDY BUDDIES" + LF
	receipt += str(data['date']) + LF + LF
	
	receipt += L_ALIGN

	# Print data
	receipt += "\x1b\x45Name:\x1b\x46 {}".format(' '.join([person.first_name,person.last_name])) + LF
	receipt += "\x1b\x45Grade:\x1b\x46 {}".format(person.grade) + LF
	receipt += "\x1b\x45In Time:\x1b\x46 {}".format("3:05pm") + LF
	receipt += "\x1b\x45Out Time:\x1b\x46 {}".format("4:41pm") + LF
	receipt += "\x1b\x45Total Hours:\x1b\x46 1" + LF
	receipt += "\x1b\x45Subjects:\x1b\x46" + LF
	# receipt += ESC + '\x44\x00
	receipt += "     \x1b\x45Math:\x1b\x46 48 min" + LF
	receipt += "     \x1b\x45Science:\x1b\x46 58 min" + LF + LF + LF + LF

	# receipt += ESC + 'b' + '413\x00' + "100497\x00"

	# receipt += ESC + '\x62\x34' + chr(51) + chr(49) + chr(55) + "12637916293671263816" + '\x1e'

	# Add footer
	receipt += C_ALIGN
	receipt += "ATTENTION STUDENTS!" + LF + "After you show this ticket" + LF 
	receipt += "to your parents and teachers," + LF
	receipt += "bring it by SS2 during lunch to" + LF
	receipt += "enter in the Study Buddies raffle!" + LF + LF
	#			ESC  b   n1  n2  n3  n4
	receipt += "\x1b\x62\x06\x01\x02\x4012345\x1e\r\n"
	receipt += "powered by Javelin" + LF
	receipt += "(c) 2013 Jacobson & Varni" + LF + LF

	receipt += CUT
	receipt += RESET

	return dict(receipt=receipt.encode('hex'))



# applet.useAlternatePrinting(true);
# applet.append("\x1b\x40");
# applet.append("\x1b\x1d\x61\x31");
# applet.append("\x1b\x4b" + image.);
# applet.append("STUDY BUDDIES" + "\x0a");
# applet.append("August 26, 2013" + "\x0a");
# applet.append("\x1b\x1d\x61\x30" + "\x0a");
# applet.append("Name: Jeremy Jacobson" + "\x0a");
# applet.append("Grade: 15" + "\x0a");
# applet.append("Subjects: Math, CS" + "\x0a");
# applet.append("\x1b\x1d\x61\x31");
# applet.append("powered by Javelin" + "\x0a");
# applet.append("(c)2013 Jacobson & Varni" + "\0xa");
# applet.append("\x0a\x0a\x0a");
# applet.append("\x1b\x64\x33");
# applet.append("\x1b\x40");
# applet.print();
# return;

# @auth.requires_login()
# @service.json
# def dates(offset):
# 	"""
# 		:param offset: Timezone offset in minutes
# 	"""
# 	minimum = db.sb_att.in_time.min()
# 	earliest = db().select(minimum).first()
	
# 	dates = list()
# 	if earliest:
# 		now = request.now
# 		numdays = (now - earliest).days
# 		for x in range(numdays):
# 			new = earliest - datetime.timedelta(minutes=offset) + datetime.timedelta(days=x)
# 			dates.append(dict(label=new.strftime('%B %d, %Y'), value=new.strftime('%Y-%m-%d-%H-%M-%S')))
# 	else:
# 		new = now - datetime.timedelta(minutes=offset)
# 		dates.append(dict(label=new.strftime('%B %d, %Y'), value=new.strftime('%Y-%m-%d-%H-%M-%S')))

# 	return dates

def is_in_day(time, date):
	start = datetime.datetime(date.year, date.month, date.day)
	end = start + datetime.timedelta(1)
	return True if (time >= start and time < end) else False

def calc_hour(in_time):
	diff = request.now - in_time
	mins = divmod(diff.days * 86400 + diff.seconds, 60)[0]
	hours = mins*1.0/60.0
	if hours > 1.9 and hours < 3:
		hours = 2
	elif hours < 1.9 and hours > 0.9:
		hours = 1
	else:
		hours = 0
	return hours

def user():
	"""
	exposes:
	http://..../[app]/default/user/login
	http://..../[app]/default/user/logout
	http://..../[app]/default/user/register
	http://..../[app]/default/user/profile
	http://..../[app]/default/user/retrieve_password
	http://..../[app]/default/user/change_password
	http://..../[app]/default/user/manage_users (requires membership in 
	use @auth.requires_login()
		@auth.requires_membership('group name')
		@auth.requires_permission('read','table name',record_id)
	to decorate functions that need access control
	"""

	form = auth()
	if request.args(0)=='login':
		login_form = auth.login()
		form = FORM(
				FIELDSET(
					DIV(
						INPUT(_type='text', _name='username', 
							_id='auth_user_username', _placeholder="Username", 
							_class="form-control"),
						_class="form-group"
					),
					DIV(
						INPUT(_type='password', _name='password', 
							_id='auth_user_password', _placeholder="Password", _class="form-control"),
						_class="form-group"
					)
				),
				DIV(
					INPUT(_type='submit', _value="Login", _class='btn btn-primary btn-lg btn-block'),
					_class="form-group"
				),
				DIV(
					INPUT(_type='button', 
						_onclick="window.location='{}';return false".format(
							URL(args='register', vars={'_next': request.vars._next} 
								if request.vars._next else None)),
						_value='Register', _class='btn btn-default pull-left'),
					INPUT(_type='button', _onclick="window.location='{}';return false".format(URL(args='request_reset_password')),
						_value='Lost Password', _class='btn btn-default pull-right', _style='margin-right: 0'),
					_class="form-group"
				),
				_role="form"
			)
		form.append(login_form.custom.end)

		# if not 'register' in auth.settings.actions_disabled:
		# 	form.add_button(T('Register'),URL(args='register', vars={'_next': request.vars._next} if request.vars._next else None),_class='btn')

		# if not 'request_reset_password' in auth.settings.actions_disabled:
		# 	form.add_button(T('Lost Password'),URL(args='request_reset_password'),_class='btn')

	return dict(form=form)

@cache.action()
def download():
	"""
	allows downloading of uploaded files
	http://..../[app]/default/download/[filename]
	"""
	return response.download(request, db)


@auth.requires_login()
def call():
	"""
	exposes services. for example:
	http://..../[app]/default/call/jsonrpc
	decorate with @services.jsonrpc the functions to expose
	supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
	"""
	return service()


@auth.requires_signature()
def data():
	"""
	http://..../[app]/default/data/tables
	http://..../[app]/default/data/create/[table]
	http://..../[app]/default/data/read/[table]/[id]
	http://..../[app]/default/data/update/[table]/[id]
	http://..../[app]/default/data/delete/[table]/[id]
	http://..../[app]/default/data/select/[table]
	http://..../[app]/default/data/search/[table]
	but URLs must be signed, i.e. linked with
	  A('table',_href=URL('data/tables',user_signature=True))
	or with the signed load operator
	  LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
	"""
	return dict(form=crud())
