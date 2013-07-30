@auth.requires_login()
@auth.requires_membership('admin')
@service.json
def make_pdf_from_html(filename='labels.pdf', year='2013'):
	import time
	import os
	filename = "{}/applications/javelin/static/{}_{}".format(os.getcwd(), int(time.time()), filename)
	# output = open(filename, "w+b")

	from xhtml2pdf import pisa

	# from pyfpdf import FPDF, HTMLMixin
	# class PDF(FPDF, HTMLMixin):
	# 	def __init__(self, *args, **kwargs):
	# 		super(PDF, self).__init__(*args, **kwargs)

	table_temp = """<table style="font-family: 'Times New Roman'">
		<tbody>
			{0}
			{1}
			{2}
			{3}
			{4}
		</tbody>
	</table>
	"""

	row_temp = """		<tr style="width: 100%">
				{0}
				<td style="width: .19in; height: 2in"></td>
				{1}
			</tr>
	"""

	label_temp = """			<td style="width: 4in; height: 2in">
					<div style="height:100%; padding: 10px;">
						<div style="float: left; margin-top: 10px; margin-left: 10px; width: auto">
							<img src="static/images/vc2emblem.png" style="height: 50px; width: 50px">
						</div>
						<div style="float: right; margin-top:10px; margin-right: 10px; width: auto">
							<img src="static/images/vc2emblem.png" style="height: 50px; width: 50px">
						</div>
						<div style="text-align: center"><b>{year} Freshmen Orientation</b></div>
						<div style="text-align: center; margin-top: 10px"><b style="font-size: 24pt">{first_name}</b></div>
						<div style="text-align: center; margin-top: 5px">{last_name}</div>
						<div style="margin-top: 10px">
							<span>ID#: {id}</span><br>
							<span>Crew#: {crew}</span><br>
							<span>Crew Room: {crew_room}</span><br>
							<span>W.E.F.S.K. Rotation: {wefsk}</span><br>
						</div>
					</div>
				</td>
	"""

	people = db().select(db.person.ALL).as_list()

	# pdf = PDF(format='letter')
	row_num = 0
	label_num = 0
	tables = list()
	rows = list()
	labels = list()
	for person in people:
		if row_num == 5:
			tables.append(table_temp.format(*rows))
			# pdf.add_page()
			rows = list()
			row_num = 0
		
		if label_num == 2:
			rows.append(row_temp.format(*labels))
			labels = list()
			row_num += 1
			label_num = 0

		labels.append(label_temp.format(year=year, id=person['id'], 
			first_name=person['first_name'], last_name=person['last_name'], crew=0,
			crew_room='N/A', wefsk='N/A'))

		label_num += 1

	if row_num < 5:
		for i in range(5 - row_num):
			rows.append(label_temp.format(year=year, id='', 
				first_name='', last_name='', crew='',
				crew_room='', wefsk=''))
		tables.append(table_temp.format(*rows))

	html = """<style>
		@page {
			size: letter portrait;
			margin: 0.5in 0.16in 0in 0.16in;
		}
	</style>
	"""

	for table in tables:
		html += table
	
	# status = pisa.CreatePDF(html, dest=output)
	# output.close()

	return dict(response=html)