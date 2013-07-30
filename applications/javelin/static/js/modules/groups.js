var recordDataSource;

function initGroupTable() {
	$('#groups-table').datagrid({
		dataSource: new GroupDataSource({
			columns: [
				{
					property: 'name',
					label: 'Name',
					sortable: true
				},
				{
					property: 'description',
					label: 'Description',
					sortable: true
				},
				{
					property: 'actions',
					label: 'Actions',
					sortable: false
				}
			]
		}),
		stretchHeight: true
	});

	$('#group-pagesize').select2();
	$('#group-page-select').select2();
}

function initRecordsTable() {
	recordDataSource = new GroupRecDataSource({
		columns: [
			{
				property: 'id',
				label: 'ID',
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
			},
			{
				property: 'actions',
				label: 'Actions',
				sortable: false
			}
		],
		group_id: '0'
	});

	$('#records-table').datagrid({
		dataSource: recordDataSource,
		stretchHeight: true
	});
}

function loadRecordsTable(id) {
	recordDataSource._group_id = id;

	$('div[id^="records-for-"]').attr("id", "records-for-" + id);

	$('#records-table').datagrid('reload');

	$('#rec-pagesize').select2('destroy');
	$('#rec-page-select').select2('destroy');

	$('#rec-pagesize').select2();
	$('#rec-page-select').select2();
}

function addGroup(name, description, values) {
	$.ajax({
		type: "POST",
		url: "/groups/call/json/add_group",
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

				$('#groups-table').datagrid('reload');
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

function addPerson() {
	var p_id = $('#people-type-id').val();
	var g_id = $('div[id^="records-for-"]').attr("id").match(/[\d]+/);
	var person_name = $('#people-type-name').val();

	if (p_id != null && name != null) {
		$.ajax({
			type: "POST",
			url: "/groups/call/json/add_to_group",
			data: {
				"person_id" : p_id,
				"group_id" : g_id[0]
			},
			success: function() {
				$("#delete-person-modal").modal("hide");
				$("#delete-person-done-btn").attr("href", "#");
				displaySuccess("The group has been deleted.");
			
				$('#groups-table').datagrid('reload');

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
		url: "/groups/call/json/edit_group",
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

				$('#groups-table').datagrid('reload');
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
		url: "/groups/call/json/delete_group",
		data: {
			"id" : id
		},
		dataType: "json",
		success: function() {
			$("#delete-group-modal").modal("hide");
			$("#delete-done-btn").attr("href", "#");
			displaySuccess("The group has been deleted.");
		
			$('#groups-table').datagrid('reload');
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
		url: "/groups/call/json/delete_from_group",
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

			$('#records-table').datagrid('reload');
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

	$('#groups-div').height($(window).height()*.6);
	$('#records-div').height($(window).height()*.6);

	$('#groups-table').on('loaded', function() {
		$('#groups-div .grid-pagesize').select2('destroy');
		$('#groups-div .grid-pager select').select2('destroy');

		$('#groups-div .grid-pagesize').select2();
		$('#groups-div .grid-pager select').select2({ placeholder: "1" });

		$('#groups-table tbody td:last-child').each(function(index, el) {
			var id = $(el).parent().attr('id');
			$(this).html('<button class="btn btn-primary" id="edit-row-' + id + '">' +
				'<i class="icon-edit"></i>Edit' +
			'</button>' +
			'<button class="btn btn-danger" id="delete-row-' + id + '" style="margin-left: 10px">' +
				'<i class="icon-trash"></i>Delete' + 
			'</button>')
		});
						
	});

	$('#records-table').on('loaded', function() {
		var rowCount = $('#record-table').find('tr').length;
		if (rowCount == 1) {
			$('#no-rows-alert').css("display", "block");
		} else {
			$('#no-rows-alert').css("display", "none");
		}
	})

	$('#main-container').on('slid', '', function() {
		$('#prev-button').removeClass('disabled');
		$('#add-group-btn').removeClass('disabled');

		if ($('.carousel-inner .item:first').hasClass('active')) {
			$('#prev-button').addClass('disabled');
			$('#groups-table').datagrid('reload');
		} else if ($('.carousel-inner .item:last').hasClass('active')) {
			$('#add-group-btn').addClass('disabled');
			// $('#records-table').datagrid('reload');
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
		// 	e.preventDefault();

		// 	$('#people-select').pickList();
		// 	$("#people-select").html("");
		// 	$("#people-select").pickList("destroy");

		// 	$.ajaxSetup( { "async": false } );
		// 	$.getJSON("/groups/call/json/get_people", function(data) {
		// 		$.each(data, function(i, entry) {
		// 			$("#people-select").append('<option value="' + entry.value + '">' + entry.label + "</option>");
		// 		});
		// 	});
		// 	$.ajaxSetup( { "async": true } );

		// 	$('#people-select').pickList({
		// 		sourceListLabel: "People",
		// 		targetListLabel: "Added",
		// 		addAllLabel: '<i class="icon-chevron-right" style="padding: 0"></i><i class="icon-chevron-right" style="padding: 0"></i>',
		// 		addLabel: '<i class="icon-chevron-right" style="padding: 0"></i>',
		// 		removeAllLabel: '<i class="icon-chevron-left" style="padding: 0"></i><i class="icon-chevron-left" style="padding: 0"></i>',
		// 		removeLabel: '<i class="icon-chevron-left" style="padding: 0"></i>',
		// 		sortAttribute: "label"
		// 	});

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

	$('#groups-div').on('click', '#groups-table tr td:not(:last-child)', function() {
		// row was clicked
		if ($(this).html() !== "0 items") {
			var id = $(this).parent().attr("id");
			var name = $(this).parent().find("td").eq(0).html();

			$('#group-legend').html(name);

			loadRecordsTable(id);

			$('#main-container').carousel('next');
			$('#main-container').carousel('pause');
		} else {
			console.log("OOPS");
		}
	});

	$('#groups-div').on('click', '#groups-table td button[id^="delete-row"]', function(e) {
		var id = $(this).attr('id').match(/[\d]+/);
		var name = $(this).parent().parent().find("td").eq(0).html();

		$("#group-name-delete").html(name);
		$("#delete-done-btn").attr("data-group", id);
		$("#delete-group-modal").modal("show");
	});

	$('#groups-div').on('click', '#groups-table td button[id^="edit-row"]', function(e) {
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

	$('#add-person-btn').on('click', addPerson);

	$('#delete-done-btn').on('click', function() {
		var id = $(this).attr('data-group');
		deleteGroup(id);
	});

	$('#delete-person-done-btn').on('click', function() {
		var p_id = $(this).attr('data-person');
		var g_id = $(this).attr('data-group');
		deletePersonFromGroup(p_id, g_id);
	});
});

$(document).on('mouseleave', '.carousel', function() {
	$(this).carousel('pause');
});