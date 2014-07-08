from gluon.dal import Row, Rows
import phonenumbers

def resolve_refs(self, foreign_key, foreign_table):

	if isinstance(self, Row):
		pass
	elif isinstance(self, Rows):
		for i, row in enumerate(self.records):
			self.records[i] = self.db[foreign_table](row[foreign_key])

def custom_json(o):
    if hasattr(o, 'custom_json') and callable(o.custom_json):
        return o.custom_json()
    if isinstance(o, (datetime.date,
                      datetime.datetime,
                      datetime.time)):
        return o.isoformat()[:19] + 'Z'
    elif isinstance(o, (int, long)):
        return int(o)
    elif isinstance(o, decimal.Decimal):
        return str(o)
    elif isinstance(o, lazyT):
        return str(o)
    elif isinstance(o, XmlComponent):
        return str(o)
    elif hasattr(o, 'as_list') and callable(o.as_list):
        return o.as_list()
    elif hasattr(o, 'as_dict') and callable(o.as_dict):
        return o.as_dict()
    else:
        raise TypeError(repr(o) + " is not JSON serializable")


class IS_PHONE_NUMBER:
	def __init__(self, error_message="{} is not a valid phone number"):
		self.err = error_message

	def __call__(self, value):
		val = None
		err = None

		try:
			parsed = phonenumbers.parse(value, 'US')

			if phonenumbers.is_valid_number(parsed):
				val = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)
			else:
				val = value
				err = self.err.format(value)

		except phonenumbers.phonenumberutil.NumberParseException as e:
			err = e.message
			val = value

		return (val, err)

class IS_ALPHA:
	def __init__(self, error_message="{} is not alphabetic"):
		self.err = error_message

	def __call__(self, value):
		try:
			if str(value).isalpha():
				return (str(value), None)
			return (value, self.err.format(value))
		except:
			return (value, self.err.format(value))
