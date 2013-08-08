function approveUser(id) {
	$.ajax({
		type: 'POST',
		url: '/jadmin/call/json/approve_user',
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
		url: '/jadmin/call/json/disapprove_user',
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
		url: '/jadmin/call/json/import_from_query',
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

$(function() {
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
				url: '/jadmin/call/json/update_names',
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