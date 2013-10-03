var eventsTable = undefined;
var attendanceTable = undefined;

$(function() {

	/************* CALENDAR *************/

	$('#calendar').fullCalendar({
		header: {
			left: 'agendaDay,agendaWeek,month',
			center: 'title'
		},
		editable: true,
		eventSources: [
			{
				url: "/demo/events/call/json/data",
				error: function() {
					console.log('Could not retrieve events');
				}
			}
		],
		eventClick: function(calEvent, jsEvent, view) {
			console.log(calEvent);
			$('#event-title').html((calEvent.title !== "") ? calEvent.title : "No Event Title");
			$('#start-time').html(calEvent.start.toLocaleDateString() + " " + calEvent.start.toLocaleTimeString());
			$('#end-time').html(calEvent.end.toLocaleDateString() + " " + calEvent.end.toLocaleTimeString());
			$('#all-day-switch').bootstrapSwitch('setState', calEvent.allDay);
			$('#delete-event-btn').attr('data-event-id', calEvent.id);
			$('#edit-event-modal').modal('show');
		}
	});
	
	$("#inputFrom").datetimepicker({
		autoclose: true,
		showMeridian: true,
		format: 'm/d/yyyy H:ii:ss P'
	}).on('changeDate', function(ev) {
		var currentDate = new Date();
		var date = new Date(ev.date.valueOf() + currentDate.getTimezoneOffset()*60000);
		date.setSeconds(0);
		var fromTimestamp = parseInt(date.getTime()/1000);

		$('#inputFrom').attr('data-time', fromTimestamp);

		var toTimestamp = parseInt($('#inputTo').attr('data-time'));
		if (fromTimestamp > toTimestamp) {
			date.setHours(date.getHours() + 1);
			$('#inputTo').val(date.toLocaleDateString() + " " + date.toLocaleTimeString());
			$('#inputTo').attr('data-time', parseInt(date.getTime()/1000));
		}
	});

 	$("#inputTo").datetimepicker({
		autoclose: true,
		showMeridian: true,
		format: 'm/d/yyyy H:ii:ss P'
	}).on('changeDate', function(ev) {
		var currentDate = new Date();
		var date = new Date(ev.date.valueOf() + currentDate.getTimezoneOffset()*60000);
		date.setSeconds(0);
		var toTimestamp = parseInt(date.getTime()/1000);

		$('#inputTo').attr('data-time', toTimestamp);

		var fromTimestamp = parseInt($('#inputFrom').attr('data-time'));
		if (toTimestamp < fromTimestamp) {
			date.setHours(date.getHours() - 1);
			$('#inputFrom').val(date.toLocaleDateString() + " " + date.toLocaleTimeString());
			$('#inputFrom').attr('data-time', parseInt(date.getTime()/1000));
		}
	});

	$('#inputTitle').on('keyup', function() {
		$('#add-complete-btn').removeClass('disabled');

		var val = $('#inputTitle').val();
		if (val === '' || val === null) {
			$('#add-complete-btn').addClass('disabled');
		}
	});

	$('#add-event-btn').on('click', function() {
		$('#inputTitle').val('');
		$('#inputNotes').val('');
		$('#inputAllDay').bootstrapSwitch('setState', false);

		var currentDate = new Date();
		currentDate.setMinutes(parseInt(currentDate.getMinutes()/5)*5);
		currentDate.setSeconds(0);
		$('#inputFrom').attr('data-time', parseInt(currentDate.getTime()/1000));
		$('#inputFrom').val(currentDate.toLocaleDateString() + " " + currentDate.toLocaleTimeString());
		
		currentDate.setHours(currentDate.getHours() + 1);
		$('#inputTo').attr('data-time', parseInt(currentDate.getTime()/1000));
		$('#inputTo').val(currentDate.toLocaleDateString() + " " + currentDate.toLocaleTimeString());

		$('.datetimepicker th').removeClass('has-switch');

		$('#add-event-modal').modal('show');
	});

	$('#add-complete-btn').on('click', function() {
		if (!$(this).hasClass("disabled")) {
			var title = $('#inputTitle').val();
			var start = $('#inputFrom').attr('data-time');
			var end = $('#inputTo').attr('data-time');
			var notes = $('#inputNotes').val();
			var allDay = $('#inputAllDay').bootstrapSwitch('status');
			addEvent(title, start, end, notes, allDay);
		}
	});

	$('#delete-event-btn').on('click', function() {
		var title = $('#event-title').html();
		// if (title === "No Event Title")
		// 	title = "";
		$('#event-to-delete').html(title);
		$('#delete-confirm-btn').attr('data-event-id', $(this).attr('data-event-id'));
		$('#edit-event-modal').modal('hide');
		$('#delete-event-modal').modal('show');
	});

	$('#delete-confirm-btn').on('click', function() {
		var id = $(this).attr('data-event-id');
		deleteEvent(id);
	});

	/************* ATTENDANCE *************/

	setInterval(reloadAttendance, 5000);

	eventsTable = $('#events-table').jTable({
		columns: [
			{'key': 'id', 'label': 'ID'},
			{'key': 'title', 'label': 'Title'},
			{'key': 'start_time', 'label': 'From'},
			{'key': 'end_time', 'label': 'To'}
		],
		title: 'Events',
		pageSize: 100,
		ajax: {
			source: "/demo/events/call/json/data"
		},
		createdRow: function(row, data) {
			$(row).attr("id", data['id']);

			var startDate = new Date(data.start_time*1000);
			var endDate = new Date(data.end_time*1000);

			$('td:eq(2)', row).html(startDate.toLocaleDateString() + " " + startDate.toLocaleTimeString());
			$('td:eq(3)', row).html(endDate.toLocaleDateString() + " " + endDate.toLocaleTimeString());
			
			$('td:eq(4)', row).html((data.allDay) ? "Yes" : "No");

			return row;
		}
	});

	attendanceTable = $('#attendance-table').jTable({
		columns: [
			{'key': 'id', 'label': 'ID'},
			{'key': 'person_student_id', 'label': 'Stud.ID'},
			{'key': 'person_last_name', 'label': 'Last Name'},
			{'key': 'person_first_name', 'label': 'First Name'},
			{'key': 'attendance_present', 'label': 'Present?'}
		],
		title: "Attendance",
		pageSize: 100,
		ajax: {
			source: "/demo/events/call/json/attendance_data",
			data: {
				event_id: 0
			},
			error: function() {
				displayError("Could not load events.");
			}
		},
		createdRow: function(row, data) {
			$(row).attr("id", data['id']);

			var id = data['id']
			var present = (data['attendance_present']) ? true : false;
			var checkbox = $('<div class="switch switch-small" id="present-check-' + id + 
				'" data-on-label="YES" data-off-label="NO"><input type="checkbox"' + ((present) ? 'checked' : '') + '></div>');
			
			checkbox.find('input:checkbox').prop('checked', present);
			$('td:eq(4)', row).html(checkbox);
			checkbox.bootstrapSwitch().on('switch-change', function(e, data) {
				var event_id = attendanceTable._event_id;
				var person_id = $(data.el).parent().parent().parent().parent().attr("id");
				var present = data.value;
				quickAttendance(person_id, event_id, present, false);
			});

			return row;
		},
		filter: {
			fn: function(value, data) {
				return _.filter(data, function (item) {
					switch(value) {
						case 'leaders':
							if(item.person_grade != 9 && item.person_leader) return true;
							break;
						case 'freshmen':
							if(item.person_grade == 9) return true;
							break;
						default:
							return true;
							break;
					}
				});
			},
			options: [
				{'value': 'all','label': 'All'},
				{'value': 'leaders','label': 'Leaders'},
				{'value': 'freshmen','label': 'Freshmen'}
			],
			class: 'select2'
		}
	});

	$('.select2').select2();

	$(document).on('mouseleave', '.carousel', function() {
		$(this).carousel('pause');
	});

	$('#events-div').on('click', '#events-table tr td', function() {
		// row was clicked
		if ($(this).html() !== "0 items") {
			var event_id = $(this).parent().attr("id");
			var title = $(this).parent().find('td').eq(1).html();

			$('#main-container').carousel('next');
			$('#main-container').carousel('pause');

			setTimeout(loadRecord(event_id, title), 100);
		}
	});

	$('#main-container').on('slid', function() {
		$('.carousel-inner').css('overflow', 'visible');
		$('#prev-button').removeClass('disabled');
		$('#quick-att-btn').removeClass('disabled');
		
		if ($('#main-container .carousel-inner .item:first').hasClass('active')) {
			$('#prev-button').addClass('disabled');
			eventsTable.jTable('reload');
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

	$('#prev-button').on('click', function(e) {
		if($(this).hasClass('disabled')) {
			 e.preventDefault();
			 return false;
		} else {
			$('#main-container').carousel('prev');
		}
	});

	// $('.nav-pills li a').on('click', function() {
	// 	var href = $(this).attr('href');
	// 	$('#prev-button').removeClass('disabled');
	// 	$('#quick-att-btn').removeClass('disabled');

	// 	if (href == '#attendance') {
	// 		if ($('#main-container .carousel-inner .item:first').hasClass('active')) {
	// 			$('#prev-button').addClass('disabled');
	// 			eventsTable.jTable('reload');
	// 			$('#quick-att-input').attr('readonly', true);
	// 			$('#quick-att-btn').addClass('disabled');
	// 		} 
	// 		else if ($('#main-container .carousel-inner .item:last').hasClass('active')) {
	// 			$('#quick-att-input').attr('readonly', false);
	// 		}
	// 	} else {

	// 	}
	// });

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
		var student_id = $('#quick-att-input').val();
		var event_id = $('div[id^="attendance-for-"]').attr("id").match(/[\d]+/)[0];
		$('#quick-att-input').val('');
		$('#quick-att-btn').addClass('disabled');
		quickAttendance(student_id, event_id, true, true);
	});

	$('.nav li a').on('click', function() {
		var href = $(this).attr('href');
		if (href == "#attendance") {
			// attendanceTable.jTable('reload');
			$('#attendance-nav').fadeIn(500).css('display', 'block');
			$('#cal-nav').fadeOut(500).css('display', 'none');
		} else {
			$('#attendance-nav').fadeOut(500).css('display', 'none');
			$('#cal-nav').fadeIn(500).css('display', 'block');
		}
	});

	// $('#quick-att-input').tooltip({'trigger':'manual', 'title': 'Please choose an event', 'placement': 'bottom'});
	// $('#quick-att-input').on('mouseover', function() {
	// 	if (this.readOnly) {
	// 		$(this).tooltip('show');
	// 	}
	// });

	// $('#quick-att-input').on('mouseleave', function() {
	// 	$(this).tooltip('hide');
	// });
});

/************* CALENDAR *************/

function addEvent(title, start, end, notes, allDay) {
	$.ajax({
		type: 'POST',
		url: '/demo/events/call/json/add_event',
		data: {
			'title' : title,
			'start' : start,
			'end' : end,
			'notes' : notes,
			'allDay' : allDay
		},
		dataType: 'json',
		success: function(data) {
			if (!data.exists) {
				$('#add-event-modal').modal('hide');
				$('#calendar').fullCalendar('refetchEvents');
				displaySuccess("The event has been added.");
			} else {
				displayError("Could not add event. An event already exists with that name.", true);
			}
		},
		error: function() {
			displayError("Could not add event. There was a server or database error.", true);
		}
	})
}

function deleteEvent(id) {
	$.ajax({
		type: 'POST',
		url: '/demo/events/call/json/delete_event',
		data: {
			'id' : id
		},
		dataType: 'json',
		success: function(data) {
			$('#delete-event-modal').modal('hide');
			$('#calendar').fullCalendar('refetchEvents');
			displaySuccess("The event has been deleted.");
		},
		error: function() {
			displayError("Could not delete the event. There was a server or database error.", true);
		}
	});
}

function renderPersonDropdown() {
	var header = $('#schedule-calendar td.fc-header-left');
	var input = $('<input id="person-dropdown" type="hidden" class="span12"/>');
	if (header.find('input').length == 0)
		header.append(input);
	input.select2({
		placeholder: "Search for people",
		id: function(person) { return person['id'] },
		minimumInputLength: 3,
		ajax: {
			type: 'POST',
			url: '/people/data',
			dataType: 'json',
			quietMillis: 100,
			data: function(term, page) {
				return { filter: term };
			},
			results: function(data, page) {
				return { results: data };
			}
		},
		formatResult: function(person) {
			return person['last_name'] + ', ' + person['first_name'];
		},
		formatSelection: function(person) {
			console.log(person['id']);
			return person['last_name'] + ', ' + person['first_name'];
		}
	});
}

/************* ATTENDANCE *************/

function loadRecord(event_id, event_title) {
	attendanceTable._event_id = event_id;

	$('div[id^="attendance-for-"]').attr("id", "attendance-for-" + event_id);
	attendanceTable.jTable('setTitle', event_title);

	attendanceTable.jTable('reload', {data: {event_id: parseInt(event_id)}});
}

function quickAttendance(person_id, event_id, present, isStudentID) {
	if (!isStudentID) {
		var data = {
			'person_id': person_id,
			'event_id': event_id,
			'present': present
		}
	} else {
		var data = {
			'student_id': person_id,
			'event_id': event_id,
			'present': present
		}
	}

	$.ajax({
		type: 'POST',
		url: '/demo/events/call/json/quick_attendance',
		data: data,
		dataType: 'json',
		success: function(data) {
			if (data.error) {
				displayError('Could not take attendance for ' + ((isStudentID) ? student_id : person_id) + '.');
			}
		},
		error: function() {
			displayError('Could not take attendance for ' + ((isStudentID) ? student_id : person_id) + '.');
		}
	});
}

function reloadAttendance() {
	if ($('#main-container .carousel-inner .item:last').hasClass('active') && $('.nav-pills li.active a').attr('href') == "#attendance") {
		attendanceTable.jTable('seamlessReload');
	}
}