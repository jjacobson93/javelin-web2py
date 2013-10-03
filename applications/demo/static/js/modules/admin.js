var DOC_TYPES = {
	CALLSLIP: {value: 0, label: "Call Slips"},
	ATTSHEETS: {value: 1, label: "Attendance Sheets"},
	NAMETAGS: {value: 2, label: "Nametags"}
}

function approveUser(id) {
	$.ajax({
		type: 'POST',
		url: '/demo/jadmin/call/json/approve_user',
		data: {
			'id' : id
		},
		dataType: 'json',
		success: function(data) {
			displaySuccess("User has been approved");
			location.reload();
		},
		error: function() {
			displayError("User could not be approved");
		}
	});
}

function disapproveUser(id) {
	$.ajax({
		type: 'POST',
		url: '/demo/jadmin/call/json/disapprove_user',
		data: {
			'id' : id
		},
		dataType: 'json',
		success: function(data) {
			displaySuccess("User has been disapproved");
			setTimeout(location.reload(), 5000);
		},
		error: function() {
			displayError("User could not be disapproved");	
		}
	});
}

function importFromCSV(csv_file) {
	$("#import-button").button('loading');
	var leader_check = $("#leader_check").prop('checked');
	$.ajax({
		type: 'POST',
		url: '/demo/jadmin/call/json/import_from_query',
		data: {
			'csv_file': csv_file,
			'leaders': leader_check
		},
		success: function() {
			$('#import-modal').modal('hide');
			$("#import-button").button('reset');
			displaySuccess("Imported file.");
			$('.fileupload').fileupload('clear');
			$('.fileupload').fileupload('reset');
		},
		error: function() {
			displayError("Could not upload file.", true);
		}
	});
}

function handleFile(event) {
	var csv_file = event.target.result;
	importFromCSV(csv_file);
}

function createDoc(doctype, data) {
	$.ajax({
		type: "POST",
		url: "/demo/jadmin/call/json/create_doc",
		data: {
			'doctype': doctype,
			'data': JSON.stringify(data)
		},
		dataType: 'json',
		success: function(data) {
			$('#loading-doc-modal').modal('hide');
			$('#fields .form-group').slideUp(500);
			$('#create-doc-btn').addClass('disabled');
			$('#doc-type-select').select2('val','');
			$('#add-person-select').select2('val','');
			$('#eventatt_select').select2('val','');
			$('#event_name_input, #message-field').val('');
			displaySuccess('Document has been created! Downloading now.');
			window.location.href = '/download/' + data.filename;
		},
		error: function(e) {
			$('#loading-doc-modal').modal('hide');
			displayError("Could not create doc.");
		}
	});

	return false;
}

function checkFields() {
	var doctype = $('#doc-type-select').select2('val');

	$('#create-doc-btn').removeClass('disabled');

	if (doctype == DOC_TYPES.CALLSLIP.value) {
		var data = {
			people: $('#add-person-select').select2('val'),
			message: $('#message-field').val()
		};

		if (!data.people || !data.message)
			$('#create-doc-btn').addClass('disabled');
	}
	else if (doctype == DOC_TYPES.ATTSHEETS.value) {
		
	}
	else if (doctype == DOC_TYPES.NAMETAGS.value) {
		var data = {
			people: $('#add-person-select').select2('val'),
			eventname: $('#event_name_input').val(),
			attendance: $('#eventatt_select').val()
		};

		if (!data.people || !data.eventname || !data.attendance)
			$('#create-doc-btn').addClass('disabled');
	}
}

function createAddPersonSelect() {
	$.ajax({
		type: "POST",
		url: '/demo/jadmin/call/json/get_person_group_data',
		dataType: 'json',
		success: function(data) {
			var opt = ""
			$.each(data, function(i, e) {
				opt += "<optgroup label='" + e.text + "'>";
				$.each(e.children, function(i, e) {
					opt += "<option value='" + e.id + "''>" +
						e.last_name + ((e.first_name) ? (", " + e.first_name) : "") +
						"</option>";
				});
				opt += "</optgroup>";
			});
			$('#add-person-select').html(opt);
		},
		error: function() {
			displayError("Could not load people");
		}
	});

	$('#add-person-select').select2({
		placeholder: "Add Person(s)",
		// id: function(person) { 
		// 	return person['id'];
		// },
		// multiple: true,
		// minimumInputLength: 1,
		// ajax: {
		// 	type: 'POST',
		// 	url: '/demo/jadmin/call/json/get_person_group_data',
		// 	dataType: 'json',
		// 	quietMillis: 1000,
		// 	data: function(term, page) {
		// 		return { query: term };
		// 	},
		// 	results: function(data, page) {
		// 		return { results: data };
		// 	}
		// },
		// formatResult: function(record, container, query, escapeMarkup) {
		// 	var markup=[]; 

		// 	if (!record['text']) {
		// 		if (record['first_name'])
		// 			window.Select2.util.markMatch(record['last_name'] + ', ' + record['first_name'], query.term, markup, escapeMarkup); 
		// 		else
		// 			window.Select2.util.markMatch(record['last_name'], query.term, markup, escapeMarkup); 
		// 	} else {
		// 		window.Select2.util.markMatch(record['text'], query.term, markup, escapeMarkup); ;
		// 	}

		// 	return markup.join("")
		// },
		// formatSelection: function(record) {
		// 	if (!record['text']) {
		// 		if (record['first_name']) 
		// 			return record['last_name'] + ', ' + record['first_name'];
		// 		else
		// 			return record['last_name'];
		// 	} else {
		// 		return record['text'];
		// 	}
		// }
	});
}

$(function() {
	createAddPersonSelect();

	$('#doc-type-select').on('change', function(e) {
		var val = e.val;
		$('#fields .form-group').slideUp(500);
		if (val == DOC_TYPES.CALLSLIP.value) {
			$('#person-fields').slideDown(500);
		}
		else if (val == DOC_TYPES.ATTSHEETS.value) {
			$('#person-fields').slideDown(500);
		}
		else if (val == DOC_TYPES.NAMETAGS.value) {
			$('#person-fields').slideDown(500);
			$('#nametag-fields .form-group').slideDown(500);
		}
	});

	$('#add-person-select').on('change', function(e) {
		var val = e.val;
		var doctype = $('#doc-type-select').select2('val');
		if (val.length == 1 && doctype == DOC_TYPES.CALLSLIP.value) {
			$('#callslip-fields').slideDown(500);
		}
		checkFields();
	});

	$('#message-field').on('keyup', function(e) {
		checkFields();
	});

	$('#eventatt_select').on('change', function(e) {
		var val = e.val;
		if (val == -1)
			$('input[name="presentradios"]').prop('disabled', true);
		else
			$('input[name="presentradios"]').prop('disabled', false);

		checkFields();
	});

	$("#event_name_input").on("keyup", function(e) {
		checkFields();
	});

	$('#create-doc-btn').on('click', function() {
		$('#loading-doc-modal').modal('show');
		var doctype = $('#doc-type-select').select2('val');

		if (doctype == DOC_TYPES.CALLSLIP.value) {
			var data = {
				people: $('#add-person-select').select2('val'),
				message: $('#message-field').val()
			};
		}
		else if (doctype == DOC_TYPES.ATTSHEETS.value) {
			
		}
		else if (doctype == DOC_TYPES.NAMETAGS.value) {
			var data = {
				people: $('#add-person-select').select2('val'),
				event_name: $('#event_name_input').val(),
				events: $('#eventatt_select').select2('val'),
				present: $('input[name="presentradios"]:checked').val()
			};
		}

		createDoc(doctype, data);
	});

	$('select#doc-type-select').select2();
	$('select#eventatt_select').select2();

	$('#save-button').on('click', function(e) {
		e.preventDefault();
		var data = [];
		$('#modules-tbody').find('tr').each(function() {
			var name = $(this).find('td').eq(0).html();
			var value = $(this).find('input').val();
			if (value !== "")
				data.push({'name' : name.toLowerCase(), 'value' : value});
		});

		if (data.length > 0) {
			$.ajax({
				type: 'POST',
				url: '/demo/jadmin/call/json/update_names',
				data: 'names=' + JSON.stringify(data),
				dataType: 'json',
				success: function() {
					displaySuccess("The changes were saved.");
					setTimeout(function() {
					 	location.reload();
					}, 5000);
				},
				error: function() {
					displayError("The changes could not be saved");
				}
			});
		}
	});

	$('#add-user-button').on('click', function(e) {
		e.preventDefault();
		$('#add-user-modal').modal('show');
	});

	$('#import-from-csv-btn').on('click', function() {
		$('#import-modal').modal('show');
	});

	$('.fileupload').on('change', function(e) {
		$('#import-button').removeClass('disabled');
		if (e.isTrigger) {
			$('#import-button').addClass('disabled');
		}
	});

	$('#import-button').on('click', function() {
		var csv_file = document.getElementById('csv_file').files[0];
		var reader = new FileReader();
		reader.readAsText(csv_file, 'UTF-8');
		reader.onload = handleFile;
	});

	$('#organize-btn').on('click', function() {
		$('#organize-btn').button('loading');
		$.ajax({
			type: 'POST',
			url: '/orientation/call/json/organize_crews',
			data: {
				'desiredsize' : 12
			},
			success: function() {
				$('#organize-btn').button('reset');
				displaySuccess('Crews have been organized!');
			},
			error: function() {
				displayError('Could not organize crews.');
			}
		});
	});
});