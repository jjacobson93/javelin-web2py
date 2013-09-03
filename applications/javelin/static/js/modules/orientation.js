var isMovePopoverVisible = false;
var clickedAway = false;

var crewsTable = undefined;
var crewRecTable = undefined;

$(function() {

	crewsTable = $('#crews-table').jTable({
		columns: [
			{'key': 'id', 'label': 'ID'},
			{'key': 'room', 'label': 'Room'},
			{'key': 'wefsk', 'label': 'WEFSK'},
			{'key': 'count', 'label': 'Count'}
		],
		title: "Crews",
		pageSize: 100,
		ajax: {
			source: "/orientation/call/json/crews",
			error: function() {
				displayError("Could not load crews.");
			}
		},
		createdRow: function(row, data) {
			$(row).attr("id", data['id']);
			return row
		}
	});

	crewRecTable = $('#crew-records-table').jTable({
		columns: [
			{'key': 'student_id', 'label': 'ID'},
			{'key': 'last_name', 'label': 'Last Name'},
			{'key': 'first_name', 'label': 'First Name'},
			{'key': 'actions', 'label': 'Actions'}
		],
		title: 'Crew Records',
		pageSize: 25,
		ajax: {
			source: "/orientation/call/json/crew_records",
			data: {
				id: 0
			},
			error: function() {
				displayError("Could not load crew records.");
			}
		},
		createdRow: function(row, data) {
			$(row).attr("id", data['id']);

			$(row).find('button[id^="crew-move-person"]').popover({
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

			return row;
		}
	});

	$('#crew-records-table').on('click', 'td button[id^="crew-remove-person"]', function() {
		var person_id = $(this).parent().parent().attr('id');
		removeFromCrew(person_id);
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
			crewsTable.jTable('reload');
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
			$('#crews-container').carousel('prev');
		}
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

function loadCrewRecord(crew_id, room, wefsk) {
	crewRecTable._crew_id = crew_id;

	$('div[id^="crew-records-for"]').attr("id", "crew-" + crew_id);
	$('#crew-number').html(crew_id);
	$('#crew-room-field').val(room);
	$('#crew-wefsk-field').val(wefsk);

	crewRecTable.jTable('setTitle','Crew ' + crew_id);
	crewRecTable.jTable('reload', {data: {id: crew_id}});

	loadPeopleForTypeahead();
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

				crewsTable.jTable('reload');
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
			crewRecTable.jTable('reload');
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
			crewRecTable.jTable('reload');
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
			crewRecTable.jTable('reload');
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