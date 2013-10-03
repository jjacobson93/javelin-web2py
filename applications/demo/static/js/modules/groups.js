var groupsTableIsInit = false;

var groupsTable = undefined;
var recordsTable = undefined;

function initGroupTable() {
	groupsTable = $('#groups-table').jTable({
		columns: [
			{'key': 'name', 'label': 'Name'},
			{'key': 'description', 'label': 'Description'},
			{'key': 'count', 'label': 'Count'},
			{'key': 'actions', 'label': 'Actions'}
		],
		ajax: {
			source: '/demo/groups/call/json/data',
			error: function() {
				displayError("Could not load data.");
			}
		},
		title: 'Groups',
		pageSize: 100,
		createdRow: function(row, data) {
			$(row).attr('id', data['id']);
			return row;
		}
	});

	$('.table-header').css({
		'display': 'inline',
		'margin-right' : '10px',
		'font-weight': 'bold',
		'font-size': '26px'
	});
}

function initRecordsTable() {
	recordsTable = $('#records-table').jTable({
		columns: [
			{'key': 'id', 'label': 'ID'},
			{'key': 'last_name', 'label': 'Last Name'},
			{'key': 'first_name', 'label': 'First Name'},
			{'key': 'actions', 'label': 'Actions'}
		],
		ajax: {
			source: '/demo/groups/call/json/records',
			data: {
				id: 0
			},
			error: function() {
				displayError("Could not load records");
			}
		}
	});
}

function loadRecordsTable(id) {
	recordsTable._group_id = id;

	$('div[id^="records-for-"]').attr("id", "records-for-" + id);

	$('#add-person-select').select2({
		placeholder: "Add People",
		id: function(person) { 
			return person['id'];
		},
		multiple: true,
		minimumInputLength: 3,
		ajax: {
			type: 'POST',
			url: '/demo/groups/call/json/people_not_in_group',
			dataType: 'json',
			quietMillis: 100,
			data: function(term, page) {
				return { group_id: id, query: term };
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

	recordsTable.jTable('reload', {data: {id: id}});
}

function addGroup(name, description, values) {
	$.ajax({
		type: "POST",
		url: "/demo/groups/call/json/add_group",
		data: {
			'name' : name,
			'description' : description,
			'values' : JSON.stringify(values)
		},
		success: function(data) {
			if (!data.exists) {
				$('#inputName').val("");
				$('#inputDescription').val("");
				$('#add-group-modal').modal('hide');
				displaySuccess("The group has been added");

				groupsTable.jTable('reload');
			} else {
				displayError("A group with that name already exists.", true);
			}
		},
		error: function() {
			// $('#add-group-modal').modal('hide');
			displayError("Could not add group.", true);
		}
	});
}

function addPeopleToGroup(group_id, people) {
	$.ajax({
		type: "POST",
		url: "/demo/groups/call/json/add_to_group",
		data: {
			"people" : JSON.stringify(people),
			"group_id" : group_id,
			"multiple" : true
		},
		success: function() {
			$('#add-person-select').select2('val', '');
			recordsTable.jTable('reload', {data: {id: group_id}});
			displaySuccess("The person/people has been added.");
		},
		error: function() {
			displayError("Could not add to group. There was a server or database error.");
		}
	});
}

function addPerson() {
	var p_id = $('#people-type-id').val();
	var g_id = $('div[id^="records-for-"]').attr("id").match(/[\d]+/);
	var person_name = $('#people-type-name').val();

	if (p_id != null && name != null) {
		$.ajax({
			type: "POST",
			url: "/demo/groups/call/json/add_to_group",
			data: {
				"person_id" : p_id,
				"group_id" : g_id[0]
			},
			success: function() {
				$("#delete-person-modal").modal("hide");
				$("#delete-person-done-btn").attr("href", "#");
				displaySuccess("The group has been deleted.");
			
				groupsTable.jTable('reload');

			},
			error: function() {
				displayError("Could not add group. There was a server or database error.");
			}
		});
	} else {
		displayError("Could not add. Invalid ID or Name.");
	}
}

function editGroup(id) {
	var name = $('#name-field').val();
	var desc = $('#desc-field').val();

	$.ajax({
		type: "POST",
		url: "/demo/groups/call/json/edit_group",
		data: {
			"id" : id,
			"name" : name,
			"description" : desc
		},
		dataType: "json",
		success: function(data) {
			if (!data.exists) {
				$('#edit-group-modal').modal('hide');
				displaySuccess("The group has been edited.");

				groupsTable.jTable('reload');
			} else {
				displayError("Could not edit group. A group already exists with that name.", true);
			}
		},
		error: function() {
			// $("#edit-group-modal").modal("hide");
			displayError("Could not edit group. There was a server or database error.", true);
		}
	})
}

function deleteGroup(id) {
	$.ajax({
		type: "POST",
		url: "/demo/groups/call/json/delete_group",
		data: {
			"id" : id
		},
		dataType: "json",
		success: function() {
			$("#delete-group-modal").modal("hide");
			$("#delete-done-btn").attr("href", "#");
			displaySuccess("The group has been deleted.");
		
			groupsTable.jTable('reload');
		},
		error: function() {
			// $("#delete-group-modal").modal("hide");
			displayError("Could not delete group. There was a server or database error.", true);
		}
	});
}

function deletePersonFromGroup(p_id, g_id) {
	$.ajax({
		type: "POST",
		url: "/demo/groups/call/json/delete_from_group",
		data: {
			"person_id" : p_id,
			"group_id" : g_id
		},
		dataType: "json",
		success: function() {
			$("#delete-person-modal").modal("hide");
			$("#delete-person-done-btn").attr("data-group", "");
			$("#delete-person-done-btn").attr("data-person", "");
			displaySuccess("Person has been deleted from the group.");

			recordsTable.jTable('reload', {data: {id: g_id}});
		},
		error: function() {
			$("#delete-person-modal").modal("hide");
			displayError("Could not delete person from group.");
		}
	});
}

$(function() {

	initGroupTable();
	initRecordsTable();

	$('#main-container').on('slid', '', function() {
		$('#prev-button').removeClass('disabled');
		$('#add-group-btn').removeClass('disabled');

		if ($('.carousel-inner .item:first').hasClass('active')) {
			$('#prev-button').addClass('disabled');
			groupsTable.jTable('reload');
		} else if ($('.carousel-inner .item:last').hasClass('active')) {
			$('#add-group-btn').addClass('disabled');
		}
	});

	$('a').on('click', function(e) {
		if($(this).hasClass('disabled')) {
			 e.preventDefault();
			 return false;
		}
	});

	$('#add-group-btn').on('click', function(e) {
		if (!$(this).hasClass('disabled')) {
			$('#add-group-modal').modal('show');
		}
	});

	$('#add-done-btn').on('click', function(e) {
		e.preventDefault();
		var name = $('#inputName').val();
		var description = $('#inputDescription').val();
		// var selected = $('#people-select').find(':selected');
		var values = [];
		// $.each(selected, function(i, entry) {
		// 	values.push(entry.value);
		// });

		addGroup(name, description, values);
	});

	$('#groups-table').on('click', 'tr td:not(:last-child)', function() {
		// row was clicked
		if ($(this).html() != "0 items") {
			var id = $(this).parent().attr("id");
			var name = $(this).parent().find("td").eq(0).html();

			recordsTable.jTable('setTitle', name);

			loadRecordsTable(id);

			$('#main-container').carousel('next');
			$('#main-container').carousel('pause');
		} else {
			console.log("OOPS");
		}
	});

	$('#groups-table').on('click', 'td button[id^="delete-row"]', function(e) {
		var id = $(this).attr('id').match(/[\d]+/);
		var name = $(this).parent().parent().find("td").eq(0).html();

		$("#group-name-delete").html(name);
		$("#delete-done-btn").attr("data-group", id);
		$("#delete-group-modal").modal("show");
	});

	$('#groups-table').on('click', 'td button[id^="edit-row"]', function(e) {
		var id = $(this).attr('id').match(/[\d]+/);
		var name = $(this).parent().parent().find("td").eq(0).html();
		var desc = $(this).parent().parent().find("td").eq(1).html();

		$('#group-name-edit').html(name);
		$('#name-field').val(name);
		$('#desc-field').val(desc);
		$("#edit-done-btn").attr("data-group",  id);
		$("#edit-group-modal").modal("show");
	});

	$('#edit-done-btn').on('click', function() {
		var id = $(this).attr("data-group");
		editGroup(id);
	});

	$('#records-table').on('click', 'td button[id^="delete-row"]', function() {
		var p_id = $(this).attr("id").match(/[\d]+/);
		var g_id = $('div[id^="records-for-"]').attr("id").match(/[\d]+/);
		var name = $(this).parent().parent().find("td").eq(2).html() + " " + $(this).parent().parent().find("td").eq(1).html();
		var group = $('#group-legend').html();

		$('#person-name-delete').html(name);
		$('#from-group').html(group);
		$('#delete-person-done-btn').attr("data-person", p_id);
		$('#delete-person-done-btn').attr("data-group", g_id);
		$('#delete-person-modal').modal('show');
	});

	// $('#add-person-btn').on('click', addPerson);

	$('#delete-done-btn').on('click', function() {
		var id = $(this).attr('data-group');
		deleteGroup(id);
	});

	$('#delete-person-done-btn').on('click', function() {
		var p_id = $(this).attr('data-person');
		var g_id = $(this).attr('data-group');
		deletePersonFromGroup(p_id, g_id);
	});

	$('#add-person-btn').on('click', function() {
		var people = $('#add-person-select').select2('val');
		var group_id = recordsTable._group_id
		addPeopleToGroup(group_id, people);
	});
});

$(document).on('mouseleave', '.carousel', function() {
	$(this).carousel('pause');
});