var isMovePopoverVisible = false;
var clickedAway = false;

var eventsTable = undefined;
var attendanceTable = undefined;
var crewsTable = undefined;
var crewRecTable = undefined;

$(function() {

	// setInterval(reloadAttendance, 5000);

	eventsTable = $('#events-table').dataTable({
		'aoColumns': [
			{'mData' : 'id'},
			{'mData' : 'title'},
			{'mData' : 'start_time'},
			{'mData' : 'end_time'},
			{'mData' : 'allDay'}
		],
		"oLanguage": {
			"sEmptyTable": "0 items"
		},
		'sDom': "<'row'<'col-6 col-sm-6'<'#events-header'>>" +
			"<'col-6 col-sm-6'<'form-group pull-right' f>>>" +
			"<'row'<'col-12 col-sm-12'rt>><'row'<'col-6 col-sm-6'il><'col-6 col-sm-6'p>>",
		'sAjaxSource': "/events/call/json/data",
		'sAjaxDataProp' : "",
		"sPaginationType": "bootstrap",
		"bScrollCollapse": true,
		"bLengthChange": false,
		"sScrollY": "300px",
		"fnCreatedRow": function( nRow, data, iDisplayIndex, iDisplayIndexFull) {
			$(nRow).attr("id", data['id']);

			var startDate = new Date(data.start_time*1000);
			var endDate = new Date(data.end_time*1000);

			$('td:eq(2)', nRow).html(startDate.toLocaleDateString() + " " + startDate.toLocaleTimeString());
			$('td:eq(3)', nRow).html(endDate.toLocaleDateString() + " " + endDate.toLocaleTimeString());
			
			$('td:eq(4)', nRow).html((data.allDay) ? "Yes" : "No");

			return nRow;
		}
	});

	$('#events-header').css({
		'display': 'inline',
		'margin-right' : '10px',
		'font-weight': 'bold',
		'font-size': '26px'
	});

	attendanceTable = $('#attendance-table').dataTable({
		"aoColumnDefs": [
			{ "bVisible": false, "aTargets": [5,6]}
		],
		'aoColumns': [
			{'mData' : 'id'},
			{'mData' : 'person_student_id'},
			{'mData' : 'person_last_name'},
			{'mData' : 'person_first_name'},
			{'mData' : 'attendance_present'},
			{'mData' : 'person_grade'},
			{'mData' : 'person_leader'}
		],
		"oLanguage": {
			"sEmptyTable": "0 items"
		},
		'sDom': "<'row'<'col-6 col-sm-6'<'fuelux'<'select filter' <'.table-header'>>>>" +
			"<'col-6 col-sm-6'<'form-group pull-right' f>>>" +
			"<'row'<'col-12 col-sm-12'rt>><'row'<'col-6 col-sm-6'il><'col-6 col-sm-6'p>>",
		'sAjaxSource': "/orientation/call/json/attendance_data?event_id=0",
		'sAjaxDataProp' : "",
		"sPaginationType": "bootstrap",
		"bScrollCollapse": true,
		"bLengthChange": false,
		"sScrollY": "300px",
		"fnCreatedRow": function( nRow, data, iDisplayIndex, iDisplayIndexFull) {
			$(nRow).attr("id", data['id']);

			var id = data['id']
			var present = (data['attendance_present']) ? true : false;
			var checkbox = $('<div class="switch switch-small" id="present-check-' + id + 
				'" data-on-label="YES" data-off-label="NO"><input type="checkbox"' + ((present) ? 'checked' : '') + '></div>');
			
			checkbox.find('input:checkbox').prop('checked', present);
			$('td:eq(4)', nRow).html(checkbox);
			checkbox.bootstrapSwitch().on('switch-change', function(e, data) {
				var event_id = attendanceTable._event_id;
				var person_id = $(data.el).parent().parent().parent().parent().attr("id");
				var present = data.value;
				quickAttendance(person_id, event_id, present, false);
			});

			return nRow;
		}
	});

	attendanceTable.dataTableExt.afnFiltering.push(
		function( oSettings, aData, iDataIndex ) {
			if (oSettings.sTableId == 'attendance-table') {
				var value = $('.fuelux .select.filter').select('selectedItem').value;
				switch(value) {
					case 'leaders':
						if(aData[5] && aData[5] != 9 && aData[6]) return true;
						else return false;
						break;
					case 'freshmen':
						if(aData[5] && aData[5] == 9) return true;
						else return false;
						break;
					case 'non_leaders':
						if(aData[5] && aData[5] != 9 && !aData[6]) return true;
						else return false;
						break;
					default:
						return true;
						break;
				}
			} else {
				return true;
			}
		}
	);

	$('#attendance-div .table-header').html("Attendance");

	$('.fuelux .select').append("<div class='btn-group' style='margin-bottom: 8px'><button type='button' data-toggle='dropdown' class='btn btn-default dropdown-toggle' style='margin-top: -8px'>" +
		"<span class='dropdown-label'></span><span class='caret'></span></button>" + 
		"<ul class='dropdown-menu' role='menu'>" +
		"<li data-value='all'><a href='#'>All</a></li>" + 
		"<li data-value='freshmen'><a href='#'>Freshmen</a></li>" +
		"<li data-value='leaders'><a href='#'>Leaders</a></li>" + 
		"<li data-value='non_leaders'><a href='#'>Non-Leaders</a></li></ul></div>");

	$('.fuelux .select').each(function() {
		var $this = $(this);
		if ($this.data('select')) return;
			$this.select($this.data());

		$(this).on('changed', function() {
			attendanceTable.fnDraw();
		});
	});

	crewsTable = $('#crews-table').dataTable({
		'aoColumns': [
			{'mData' : 'id'},
			{'mData' : 'room'},
			{'mData' : 'wefsk'},
			{'mData' : 'count'}
		],
		"oLanguage": {
			"sEmptyTable": "0 items"
		},
		'sDom': "<'row'<'col-6 col-sm-6'<'table-header'>>" +
			"<'col-6 col-sm-6'<'form-group pull-right' f>>>" +
			"<'row'<'col-12 col-sm-12'rt>><'row'<'col-6 col-sm-6'il><'col-6 col-sm-6'p>>",
		'sAjaxSource': "/orientation/call/json/crews",
		'sAjaxDataProp' : "",
		"sPaginationType": "bootstrap",
		"bScrollCollapse": true,
		"bLengthChange": false,
		"sScrollY": "300px",
		"fnCreatedRow": function( nRow, data, iDisplayIndex, iDisplayIndexFull) {
			$(nRow).attr("id", data['id']);

			return nRow;
		}
	});

	$('#crews-div .table-header').html("Crews");

	crewRecTable = $('#crew-records-table').dataTable({
		'aoColumns': [
			{'mData' : 'student_id'},
			{'mData' : 'last_name'},
			{'mData' : 'first_name'},
			{'mData' : 'actions'}
		],
		"oLanguage": {
			"sEmptyTable": "0 items"
		},
		'sDom': "<'row'<'col-6 col-sm-6'<'table-header'>>" +
			"<'col-6 col-sm-6'<'form-group pull-right' f>>>" +
			"<'row'<'col-12 col-sm-12'rt>><'row'<'col-6 col-sm-6'il><'col-6 col-sm-6'p>>",
		'sAjaxSource': "/orientation/call/json/crew_records?id=0",
		'sAjaxDataProp' : "",
		"sPaginationType": "bootstrap",
		"bScrollCollapse": true,
		"bLengthChange": false,
		"sScrollY": "300px",
		"fnCreatedRow": function( nRow, data, iDisplayIndex, iDisplayIndexFull) {
			$(nRow).attr("id", data['id']);

			$(nRow).find('button[id^="crew-move-person"]').popover({
				trigger:'manual', 
				html: true,
				placement: 'left',
				content: function() {
					return $('<div><input type="hidden" id="change-crew-select" style="width: 100%"></div>');
				}
			}).on('click', function(e) {
				var person_id = $(this).attr("id").match(/[\d]+/);
				var current_crew = crewRecTable._crew_id;
				$('button[id^="crew-move-person"]').not(this).popover('hide');
				$(this).popover('toggle');
				$('input#change-crew-select').attr('data-person', person_id);
				$('input#change-crew-select').select2({
					placeholder: "Select Crew",
					id: function(crew) { 
						return crew['id'];
					},
					ajax: {
						type: 'POST',
						url: '/orientation/call/json/crews',
						dataType: 'json',
						quietMillis: 100,
						data: function(term) {
							return { id: term }
						},
						results: function(data, page) {
							return { results: data };
						}
					},
					formatResult: function(crew) {
						return "Crew " + crew['id'];
					},
					formatSelection: function(crew) {
						return "Crew " + crew['id'];
					}
				}).on('change', function(e) {
					var val = e.val;
					var person_id = $('input#change-crew-select').attr('data-person');
					changeToCrew(val, person_id);
				});
			});

			return nRow;
		}
	});

	$('#crew-records-table').on('click', 'td button[id^="crew-remove-person"]', function() {
		// var person_id = $(this).attr("id").match(/[\d]+/)[0];
		var person_id = $(this).parent().parent().attr('id');
		removeFromCrew(person_id);
	});

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
			eventsTable.api().ajax.reload();
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
			var room = $(this).parent().find('td').eq(1).attr('data-value');
			var wefsk = $(this).parent().find('td').eq(2).attr('data-value');

			loadCrewRecord(crew_id, room, wefsk);
			
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
			crewsTable.api().ajax.reload();
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
				eventsTable.api().ajax.reload();
				$('#quick-att-input').attr('readonly', true);
				$('#quick-att-btn').addClass('disabled');
			} 
			else if ($('#main-container .carousel-inner .item:last').hasClass('active')) {
				$('#quick-att-input').attr('readonly', false);
			}
		} else {
			if ($('#crews-container .carousel-inner .item:first').hasClass('active')) {
				$('#prev-button').addClass('disabled');
				crewsTable.api().ajax.reload();
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
		var student_id = $('#quick-att-input').val();
		var event_id = $('div[id^="attendance-for-"]').attr("id").match(/[\d]+/)[0];
		$('#quick-att-input').val('');
		$('#quick-att-btn').addClass('disabled');
		quickAttendance(student_id, event_id, true, true);
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

	$('.nav li a').on('click', function() {
		var href = $(this).attr('href');
		if (href == "#attendance") {
			attendanceTable.api().ajax.reload();
			$('#attendance-nav').fadeIn(500).css('display', 'block');
			$('#crew-nav').fadeOut(500).css('display', 'none');
		} else if (href == "#crews") {
			crewsTable.api().ajax.reload();
			$('#attendance-nav').fadeOut(500).css('display', 'none');
			$('#crew-nav').fadeIn(500).css('display', 'block');
		} else {
			$('#attendance-nav').fadeOut(500).css('display', 'none');
			$('#crew-nav').fadeOut(500).css('display', 'none');
		}
	});

	$('#nametags-btn').on('click', function() {
		var type = $('input[name="typeradios"]:checked').val().toLowerCase();
		var event_name = $('#event_name').val();
		var present = $('input[name="presentradios"]:checked').val();
		var event_id = $('#eventatt_select').val();
		$(this).button('loading');
		makeNametags(type, event_name, present, event_id);
	});

	$('#eventatt_select').on('change', function() {
		if ($(this).val() == -1)
			$('input[name="presentradios"]').prop('disabled', true);
		else
			$('input[name="presentradios"]').prop('disabled', false);
	});

	$('#att-sheets-btn').on('click', function() {
		makeAttSheets();
	});

	$('#callhome-btn').on('click', function() {
		makeCallHomes();
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

		$('.select2-search-field input').css('width', '100%');

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
		var crew_id = crewRecTable._crew_id
		addPeopleToCrew(crew_id, people);
	});

	$('#update-room-btn').on('click', function() {
		var room = $('#crew-room-field').val();
		var wefsk = $('#crew-wefsk-field').val();
		updateRoom(room, wefsk);
	});

	$(document).on('click', function(e) {
		if (!$(e.target).is('button[id^="crew-move-person"], .popover-title, ' + 
			'.popover-content, .popover-content *, .select2-drop, .select2-drop input, ' +
			'.select2-drop')) {
			$('button[id^="crew-move-person"]').popover('hide');
		}
	});
});

function loadRecord(event_id, event_title) {
	attendanceTable._event_id = event_id;

	$('div[id^="attendance-for-"]').attr("id", "attendance-for-" + event_id);
	$('#att-event-title').html(event_title);

	attendanceTable.api().ajax.url("/orientation/call/json/attendance_data?event_id="+event_id).load();
}

function loadCrewRecord(crew_id, room, wefsk) {
	crewRecTable._crew_id = crew_id;

	$('div[id^="crew-records-for"]').attr("id", "crew-" + crew_id);
	$('#crew-number').html(crew_id);
	$('#crew-room-field').val(room);
	$('#crew-wefsk-field').val(wefsk);

	crewRecTable.api().ajax.url("/orientation/call/json/crew_records?id="+crew_id).load();
	crewRecTable.fnDraw();

	$('#crew-records-div .table-header').html('Crew ' + crew_id);
	loadPeopleForTypeahead();
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
		url: '/orientation/call/json/quick_attendance',
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
		$('#attendance-table').datagrid('seamlessReload');
	}
}

function makeNametags(type, event_name, present, event_id) {
	if (present == 'null') present = null;
	else if (present == 'true') present = true;
	else if (present == 'false') present = false;

	if (event_id == -1)
		event_id = null;

	$.ajax({
		type: 'POST',
		url: '/orientation/call/json/make_labels',
		data: {
			'event_name': event_name,
			'type': type,
			'present': present,
			'event_id': event_id
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

function makeAttSheets() {
	$('#att-sheets-btn').button('loading');
	$.ajax({
		type: 'POST',
		url: '/orientation/call/json/attendance_sheet',
		data: {
			'kind': 'crew_freshmen',
		},
		dataType: 'json',
		success: function(data) {
			$('#att-sheets-btn').button('reset');
			displaySuccess("Created attendance sheets. Downloading them now.");
			var filename = data['filename'];
			window.location.href = '/download/' + filename; 
		},
		error: function() {
			displayError("Could not create attendance sheets.");
		}
	});
}

function makeCallHomes() {
	$('#callhome-btn').button('loading');
	$.ajax({
		type: 'POST',
		url: '/orientation/call/json/attendance_sheet',
		data: {
			'kind': 'call_homes',
		},
		dataType: 'json',
		success: function(data) {
			$('#callhome-btn').button('reset');
			displaySuccess("Created call homes. Downloading them now.");
			var filename = data['filename'];
			window.location.href = '/download/' + filename; 
		},
		error: function() {
			displayError("Could not create call homes.");
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
				$("#add-person-select-modal").select2("val", "");
				$('#add-crew-modal').modal('hide');
				displaySuccess("The crew has been added");

				crewsTable.api().ajax.reload();
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
			crewRecTable.api().ajax.reload();
			displaySuccess("Added people to crew");
		},
		error: function() {
			displayError("Could not add people to crew");
		}
	});
}

function removeFromCrew(person_id) {
	$.ajax({
		type: "POST",
		url: "/orientation/call/json/remove_crew",
		data: {
			'person_id': person_id
		},
		success: function() {
			crewRecTable.api().ajax.reload();
			displaySuccess("Removed from crew.");
		},
		error: function() {
			displayError("Could not remove person from crew.");
		}
	});
}

function changeToCrew(crew_id, person_id) {
	$.ajax({
		type: "POST",
		url: "/orientation/call/json/move_to_crew",
		data: {
			'person_id': person_id,
			'id': crew_id
		},
		success: function() {
			crewRecTable.api().ajax.reload();
			displaySuccess("Moved to Crew " + crew_id + ".");
		},
		error: function() {
			displayError("Could not move to Crew " + crew_id + ".");
		}
	});
}

function updateRoom(room, wefsk) {
	var id = crewRecTable._crew_id;
	$.ajax({
		type: "POST",
		url: '/orientation/call/json/update_room',
		data: {
			'id': id,
			'room' : room,
			'wefsk': wefsk
		},
		success: function() {
			displaySuccess('Room and WEFSK Rotation updated.');
		},
		error: function() {
			displaySuccess('Could not update Room and WEFSK Rotation.');
		}
	});
}

function loadPeopleForTypeahead() {
	var crew_id = crewRecTable._crew_id
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
	$('.select2-search-field input').css('width', '100%');
}