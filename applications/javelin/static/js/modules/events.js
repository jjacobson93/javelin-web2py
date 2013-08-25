$(document).ready(function() {
	$('#event-calendar').fullCalendar({
		header: {
			left: 'agendaDay,agendaWeek,month',
			center: 'title'
		},
		editable: true,
		eventSources: [
			{
				url: "/events/call/json/data",
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

	// $('#cal-tabs').on('click', 'a', function(e) {
	// 	e.preventDefault();
	// 	$(this).tab('show');
	// 	if ($(this).html().indexOf('Events') != -1) {
	// 		$('#event-calendar').fullCalendar('render');
	// 	} else if ($(this).html().indexOf('Schedules') != -1) {
	// 		$('#schedule-calendar').fullCalendar('render');
	// 		renderPersonDropdown();
	// 	}
	// });
	
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
});

function addEvent(title, start, end, notes, allDay) {
	$.ajax({
		type: 'POST',
		url: '/events/call/json/add_event',
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
				$('#event-calendar').fullCalendar('refetchEvents');
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
		url: '/events/call/json/delete_event',
		data: {
			'id' : id
		},
		dataType: 'json',
		success: function(data) {
			$('#delete-event-modal').modal('hide');
			$('#event-calendar').fullCalendar('refetchEvents');
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