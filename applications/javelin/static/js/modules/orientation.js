var attDataSource;
var crewRecDataSource;

$(function() {

	setInterval(reloadAttendance, 5000);

	$('#events-table').datagrid({
		dataSource: new EventsDataSource({
			columns: [
				{
					property: 'id',
					label: 'ID',
					sortable: true
				},
				{
					property: 'title',
					label: 'Title',
					sortable: true
				},
				{
					property: 'start_time',
					label: 'From',
					sortable: true
				},
				{
					property: 'end_time',
					label: 'To',
					sortable: true
				},
				{
					property: 'allDay',
					label: 'All Day',
					sortable: true
				}
			]
		}),
		stretchHeight: true
	});

	attDataSource = new AttendanceDataSource({
		columns: [
			{
				property: 'id',
				label: 'ID',
				sortable: true
			},
			{
				property: 'person_last_name',
				label: 'Last Name',
				sortable: true
			},
			{
				property: 'person_first_name',
				label: 'First Name',
				sortable: true
			},
			{
				property: 'attendance_present',
				label: 'Present',
				sortable: true
			}
		],
		event_id: '0'
	});

	$('#attendance-table').datagrid({
		dataSource: attDataSource,
		stretchHeight: true
	});

	$('#crews-table').datagrid({
		dataSource: new CrewDataSource({
			columns: [
				{
					property: 'id',
					label: 'ID',
					sortable: true
				},
				{
					property: 'room',
					label: 'Room',
					sortable: true
				},
				{
					property: 'wefsk',
					label: 'W.E.F.S.K Rotation',
					sortable: true
				}
			]
		}),
		stretchHeight: true
	});

	crewRecDataSource = new CrewRecordDataSource({
		columns: [
			{
				property: 'student_id',
				label: 'Student ID',
				sortable: true
			},
			{
				property: 'last_name',
				label: 'Last Name',
				sortable: true
			},
			{
				property: 'first_name',
				label: 'First Name',
				sortable: true
			}
		],
		crew_id: '0'
	});

	$('#crew-records-table').datagrid({
		dataSource: crewRecDataSource,
		stretchHeight: true
	});

	$(document).on('mouseleave', '.carousel', function() {
		$(this).carousel('pause');
	});

	$('#events-div').height($(window).height()*.6);
	$('#attendance-div').height($(window).height()*.6);
	$('#crews-div').height($(window).height()*.6);
	$('#crew-records-div').height($(window).height()*.6);

	$('#events-div').on('click', '#events-table tr td', function() {
		// row was clicked
		if ($(this).html() !== "0 items") {
			var event_id = $(this).parent().attr("id");
			var title = $(this).parent().find('td').eq(1).html();
			
			loadRecord(event_id, title);
			
			$('#main-container').carousel('next');
			$('#main-container').carousel('pause');
		}
	});

	$('#main-container').on('slid', function() {
		$('.carousel-inner').css('overflow', 'visible');
		$('#prev-button').removeClass('disabled');
		$('#quick-att-btn').removeClass('disabled');
		
		if ($('#main-container .carousel-inner .item:first').hasClass('active')) {
			$('#prev-button').addClass('disabled');
			$('#events-table').datagrid('reload');
			$('#quick-att-input').attr('readonly', true);
			$('#quick-att-btn').addClass('disabled');
		} 
		else if ($('#main-container .carousel-inner .item:last').hasClass('active')) {
			$('#quick-att-input').attr('readonly', false);
		}
	});

	$('#main-container').on('slide', function() {
		$('.carousel-inner').css('overflow', 'hidden');
	});

	$('#crews-div').on('click', '#crews-table tr td', function() {
		// row was clicked
		if ($(this).html() !== "0 items") {
			var crew_id = $(this).parent().attr("id");
			
			loadCrewRecord(crew_id);
			
			$('#crews-container').carousel('next');
			$('#crews-container').carousel('pause');
		}
	});

	$('#crews-container').on('slid', function() {
		$('#crews-container .carousel-inner').css('overflow', 'visible');
		$('#prev-button').removeClass('disabled');
		$('#add-crew-btn').removeClass('disabled');
		
		if ($('#crews-container .carousel-inner .item:first').hasClass('active')) {
			$('#prev-button').addClass('disabled');
			$('#crews-table').datagrid('reload');
		} 
		else if ($('#crews-container .carousel-inner .item:last').hasClass('active')) {
			$('#add-crew-btn').addClass('disabled');
		}
	});

	$('#crews-container').on('slide', function() {
		$(this).find('.carousel-inner').css('overflow', 'hidden');
	});
	
	$('#prev-button').on('click', function(e) {
		if($(this).hasClass('disabled')) {
			 e.preventDefault();
			 return false;
		} else {
			if ($('.nav-pills li.active a').attr('href') == "#attendance") {
				$('#main-container').carousel('prev');
			} else if ($('.nav-pills li.active a').attr('href') == "#crews") {
				$('#crews-container').carousel('prev');
			}
		}
	});

	$('.nav-pills li a').on('click', function() {
		var href = $(this).attr('href');
		$('#prev-button').removeClass('disabled');
		$('#quick-att-btn').removeClass('disabled');

		if (href == '#attendance') {
			if ($('#main-container .carousel-inner .item:first').hasClass('active')) {
				$('#prev-button').addClass('disabled');
				$('#events-table').datagrid('reload');
				$('#quick-att-input').attr('readonly', true);
				$('#quick-att-btn').addClass('disabled');
			} 
			else if ($('#main-container .carousel-inner .item:last').hasClass('active')) {
				$('#quick-att-input').attr('readonly', false);
			}
		} else {
			if ($('#crews-container .carousel-inner .item:first').hasClass('active')) {
				$('#prev-button').addClass('disabled');
				$('#crews-table').datagrid('reload');
			} 
			else if ($('#crews-container .carousel-inner .item:last').hasClass('active')) {
			}
		}
	});

	$("#quick-att-input").on('keyup', function(event){
		$('#quick-att-btn').removeClass('disabled');
		if ($(this).val() === '') {
			$('#quick-att-btn').addClass('disabled');
		}

		if (event.keyCode == 13 && $(this).val() !== ''){
			$("#quick-att-btn").click();
		} else if (event.keyCode == 13 && $(this).val() === '') {
			displayError('Invalid ID');
		}
	});

	$('#quick-att-btn').on('click', function() {
		var person_id = $('#quick-att-input').val();
		var event_id = $('div[id^="attendance-for-"]').attr("id").match(/[\d]+/)[0];
		$('#quick-att-input').val('');
		$('#quick-att-btn').addClass('disabled');
		quickAttendance(person_id, event_id);
	});

	$('#quick-att-input').tooltip({'trigger':'manual', 'title': 'Please choose an event', 'placement': 'bottom'});
	$('#quick-att-input').on('mouseover', function() {
		if (this.readOnly) {
			$(this).tooltip('show');
		}
	});

	$('#quick-att-input').on('mouseleave', function() {
		$(this).tooltip('hide');
	});

	$('div.switch[id^="present-check"]').on('click', function (e, data) {
		// var person_id = $(data.el).attr("id").match(/[\d]+/)[0];
		// var event_id = $('div[id^="attendance-for-"]').attr("id").match(/[\d]+/)[0];
		// var present = data.value;
		// quickAttendance(person_id, event_id, present);
	});

	$('#attendance-table').on('click', 'tr td:last-child', function() {
		$(this).find('input:checkbox').prop('checked', true);
	});

	$('#event-pagesize').select2();
	$('#event-page-select').select2({placeholder: "1"});
	$('#att-pagesize').select2();
	$('#att-page-select').select2({placeholder: "1"});

	$('#attendance-table').on('loaded', function() {
		if ($('#attendance-table tr').eq(1).find('td').html() != '0 items') {
			$(this).find('td:last-child').each(function(index, el) {
				var id = $(el).parent().attr('id');
				var present = ($(el).attr('data-value') == "true") ? true : false;
				var checkbox = $('<div class="switch switch-small" id="present-check-' + id + 
					'" data-on-label="YES" data-off-label="NO"><input type="checkbox"' + ((present) ? 'checked' : '') + '></div>');
				
				checkbox.find('input:checkbox').prop('checked', present);
				$(el).html(checkbox);
				checkbox.bootstrapSwitch();
			});
		}
	});

	$('.nav li a').on('click', function() {
		var href = $(this).attr('href');
		if (href == "#attendance") {
			$('#attendance-table').datagrid('reload');
			$('#attendance-nav').fadeIn(500).css('display', 'block');
			$('#crew-nav').fadeOut(500).css('display', 'none');
		} else if (href == "#crews") {
			$('#crews-table').datagrid('reload');
			$('#attendance-nav').fadeOut(500).css('display', 'none');
			$('#crew-nav').fadeIn(500).css('display', 'block');
		} else {
			$('#attendance-nav').fadeOut(500).css('display', 'none');
			$('#crew-nav').fadeOut(500).css('display', 'none');
		}
	});

	$('#nametags-btn').on('click', function() {
		var type = $('input[name="typeradios"]:checked').val();
		$(this).button('loading');
		makeNametags(type);
	});

	$('#existing-nametags-btn').on('click', function() {
		if ($(this).attr('data-state') == 'show') {
			$(this).button('hide');
			$(this).attr('data-state', 'hide');
			$('#nametags-table').slideDown(500).css('display', 'block');
		} else {
			$(this).button('show');
			$(this).attr('data-state', 'show');
			$('#nametags-table').css('display', 'none');
		}
	});

	$('#event_name').on('keyup', function() {
		var val = $(this).val();
		$('#event_name_text').html(val);
	});

	$('#add-crew-btn').on('click', function() {
		$('#add-person-select-modal').select2({
			placeholder: "Add People",
			id: function(person) { 
				return person['id'];
			},
			multiple: true,
			minimumInputLength: 3,
			ajax: {
				type: 'POST',
				url: '/orientation/call/json/people_not_in_crew',
				dataType: 'json',
				quietMillis: 100,
				data: function(term, page) {
					return { id: 0, query: term };
				},
				results: function(data, page) {
					return { results: data };
				}
			},
			formatResult: function(person) {
				return person['last_name'] + ', ' + person['first_name'];
			},
			formatSelection: function(person) {
				return person['last_name'] + ', ' + person['first_name'];
			}
		});

		$('#add-crew-modal').modal('show');
	});

	$('#add-done-btn').on('click', function() {
		var room = $('#inputRoom').val();
		var wefsk = $('#inputWefsk').val();
		var people = $('#add-person-select-modal').select2('val');

		addCrew(room, wefsk, people);
	});

	$('#add-person-btn').on('click', function() {
		var people = $('#add-person-select').select2('val');
		var crew_id = crewRecDataSource._crew_id
		addPeopleToCrew(crew_id, people);
	});

});

function loadRecord(event_id, event_title) {
	attDataSource._event_id = event_id;

	$('div[id^="attendance-for-"]').attr("id", "attendance-for-" + event_id);
	$('#att-event-title').html(event_title);

	$('#attendance-table').datagrid('reload');
}

function loadCrewRecord(crew_id) {
	crewRecDataSource._crew_id = crew_id;

	$('div[id^="crew-records-for"]').attr("id", "crew-" + crew_id);
	$('#crew-number').html(crew_id);

	$('#crew-records-table').datagrid('reload');
	loadPeopleForTypeahead();
}

function quickAttendance(person_id, event_id, present) {
	if (!present)
		present = true;

	$.ajax({
		type: 'POST',
		url: '/orientation/call/json/quick_attendance',
		data: {
			'person_id': person_id,
			'event_id': event_id,
			'present': present
		},
		dataType: 'json',
		error: function() {
			displayError('Could not take attendance for ' + person_id + '.');
		}
	});
}

function reloadAttendance() {
	if ($('.carousel-inner .item:last').hasClass('active') && $('.nav-pills li.active a').attr('href') == "#attendance" ) {
		$('#attendance-table').datagrid('seamlessReload');
	}
}

function makeNametags(type) {
	$.ajax({
		type: 'POST',
		url: '/orientation/call/json/make_labels',
		data: {
			'event_name': 'Freshmen Orientation',
			'type': type
		},
		dataType: 'json',
		success: function(data) {
			$('#nametags-btn').button('reset');
			displaySuccess("Created nametags. Downloading them now.");
			var filename = data['filename'];
			window.location.href = '/download/' + filename; 
		},
		error: function() {
			displayError("Could not create nametags.");
		}
	});
}

function addCrew(room, wefsk, people) {
	$.ajax({
		type: "POST",
		url: "/orientation/call/json/add_crew",
		data: {
			'room' : room,
			'wefsk' : wefsk,
			'people' : JSON.stringify(people)
		},
		success: function(data) {
			if (!data.exists) {
				$('#inputRoom').val("");
				$('#inputWefsk').val("");
				$('#add-crew-modal').modal('hide');
				displaySuccess("The crew has been added");

				$('#crews-table').datagrid('reload');
			} else {
				displayError("Could not add crew.", true);
			}
		},
		error: function() {
			displayError("Could not add crew.", true);
		}
	});
}

function addPeopleToCrew(id, people) {
	$.ajax({
		type: "POST",
		url: "/orientation/call/json/add_people_to_crew",
		data: {
			'id': id,
			'people': JSON.stringify(people)
		},
		success: function() {
			$("#add-person-select").select2("val", "");
			$('#crew-records-table').datagrid('reload');
			displaySuccess("Added people to crew");
		},
		error: function() {
			displayError("Could not add people to crew");
		}
	});
}

function loadPeopleForTypeahead() {
	var crew_id = crewRecDataSource._crew_id
	$('#add-person-select').select2({
		placeholder: "Add Person",
		id: function(person) { 
			return person['id'];
		},
		multiple: true,
		minimumInputLength: 3,
		ajax: {
			type: 'POST',
			url: '/orientation/call/json/people_not_in_crew',
			dataType: 'json',
			quietMillis: 100,
			data: function(term, page) {
				return { id: crew_id, query: term };
			},
			results: function(data, page) {
				return { results: data };
			}
		},
		formatResult: function(person) {
			return person['last_name'] + ', ' + person['first_name'];
		},
		formatSelection: function(person) {
			return person['last_name'] + ', ' + person['first_name'];
		}
	});
}