import random
from conf import *
from gluon.dal import DAL, Field

db = DAL(DB_URI)

db.define_table('person',
	Field('student_id', 'integer', notnull=True, unique=True),
	Field('last_name', 'string', notnull=True, required=True),
	Field('first_name', 'string', notnull=True, required=True),
	Field('home_phone', 'string'),
	Field('cell_phone', 'string'),
	Field('cell_provider', 'string'),
	Field('gender', 'string'),
	Field('email', 'string'),
	Field('street', 'string'),
	Field('city', 'string'),
	Field('state', 'string'),
	Field('zip_code', 'string'),
	Field('notes', 'string'),
	Field('pic', 'blob'),
	Field('crew', 'integer', default=None, ondelete='SET NULL'),
	Field('grade', 'integer'),
	Field('leader', 'boolean', default=False), migrate=False)

db.define_table('teacher',
	Field('teacher_id', 'integer', notnull=True, unique=True),
	Field('teacher_name', 'string', notnull=True), migrate=False)

db.define_table('dept',
	Field('title', 'string', notnull=True), migrate=False)

db.define_table('course',
	Field('course_id', 'integer', notnull=True, unique=True),
	Field('code', 'string', notnull=True),
	Field('title', 'string', notnull=True),
	Field('period', 'integer', notnull=True),
	Field('teacher_id', 'reference teacher', notnull=True),
	Field('dept_id', 'reference dept'), migrate=False)

db.define_table('course_rec',
	Field('course_id', 'reference course', notnull=True),
	Field('student_id', 'reference person', notnull=True), migrate=False)

db.define_table('grade_session',
	Field('title', 'string'), migrate=False)

db.define_table('grade',
	Field('course_rec_id', 'reference course_rec', notnull=True),
	Field('session_id', 'reference grade_session', notnull=True),
	Field('grade', 'integer', notnull=True), migrate=False)

# db.define_table('sb_section',
# 	Field('title', 'string'),
# 	Field('dept_id', 'reference dept'), migrate=False)

# db.define_table('sb_att',
# 	Field('person_id', 'reference person'),
# 	Field('sb_section_id', 'reference sb_section'),
# 	Field('in_time', 'datetime', default=request.now),
# 	Field('out_time', 'datetime', default=None, update=request.now),
# 	Field('studyhour', 'integer', default=0),
# 	Field('is_out', 'boolean', default=False), migrate=False)


FIRST_PR = 0
SECOND_PR = 1
FINAL = 2

def make_grade(session):
	if session == FIRST_PR:
		grades =  [.15,  .2,  .4,  .1,  .15]
	elif session == SECOND_PR:
		grades =  [.12,  .25,  .35,  .15,  .13]
	else:
		grades = [.08, .30, .32, .2, .1]

	x = random.random()
	if x >= 1 - grades[0]: return random.randint(10,11)
	elif x >= 1 - grades[0] - grades[1]: return random.randint(7,9)
	elif x >= 1 - grades[0] - grades[1] - grades[2]: return random.randint(4,6)
	elif x >= 1 - grades[0] - grades[1] - grades[2] - grades[3]: return random.randint(2,3)
	else: return random.randint(0,1)


people = db(db.person.id>0).select()
courses = db(db.course.id>0).select()
records = db(db.course_rec.id>0).select()
grades = db(db.grade.id>0).select(orderby=db.grade.course_rec_id)

i = 1
for g in grades:
	db(db.grade.id==g.id).update(session_id=i)
	db.commit()
	i = i%3 + 1
