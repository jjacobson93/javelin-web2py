var currentDate = new Date();
var monthNames = [ "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December" ];

function checkIn(person_id) {
	$.ajax({
		type: 'POST',
		url: '/studybuddies/call/json/checkin',
		data: {
			'person_id': person_id
		},
		dataType: 'json',
		success: function() {
			$('#checkin-input').val('');
			$('#checkin-submit').addClass('disabled');
			loadTable();
		},
		error: function() {
			displayError("Could not check in Student ID " + person_id + ".");
		}
	});
}

function checkOut(person_id) {
	var today = new Date();
	$.ajax({
		type: 'POST',
		url: '/studybuddies/call/json/checkout',
		data: {
			'person_id': person_id,
			'time_offset': today.getTimezoneOffset()
		},
		dataType: 'json',
		success: function() {
			$('#checkout-input').val('');
			$('#checkout-submit').addClass('disabled');
			loadTable();
		},
		error: function() {
			displayError("Could not check in Student ID " + person_id + ".");
		}
	});
}

function loadTable(date) {
	if (date == undefined)
		date = new Date();

	date = dateToStartEnd(date);

	$('#sb-table').html("<h1 style='text-align: center'><i class='icon-spin icon-spinner'></i> Loading...</h1>");
	$.ajax({
		type: "POST",
		url: "/studybuddies/tutors/table",
		data: {
			start: date.start,
			end: date.end
		},
		success: function(content) {
			$('#sb-table').html(content);
		},
		error: function() {
			displayError("Could not load table");
		}
	});
}

function setCurrentDate(date) {
	currentDate = date;
	var localDate = utcToLocal(date);
	$('.date-long-span').html(monthNames[localDate.getMonth()] + " " + localDate.getDate() + ", " + localDate.getFullYear());
}

$(function() {
	loadTable();

	$('#checkin-submit').on('click', function() {
		var person_id = $('#checkin-input').val();
		checkIn(person_id);
	});

	$('#checkin-input').on('keyup', function(e) {
		var val = $(this).val();
		$('#checkin-submit').removeClass('disabled');
		if (val == '')
			$('#checkin-submit').addClass('disabled');

		if (e.keyCode == 13 && val != '')
			$("#checkin-submit").click();
	});

	$('#checkout-submit').on('click', function() {
		var person_id = $('#checkout-input').val();
		checkOut(person_id, false);
	});

	$('#checkout-input').on('keyup', function(e) {
		var val = $(this).val();
		$('#checkout-submit').removeClass('disabled');
		if (val == '')
			$('#checkout-submit').addClass('disabled');

		if (e.keyCode == 13 && val != '')
			$("#checkout-submit").click();
	});

	$("#date-btn").datetimepicker({
		format: 'yyyy-mm-dd-hh-ii-ss',
		showMeridian: true,
        autoclose: true,
        todayBtn: true,
        minView: 2
	}).on('changeDate', function(ev){
		var localDate = new Date(ev.date.valueOf() + ev.date.getTimezoneOffset()*60000);
		$('.date-long-span').html(monthNames[localDate.getMonth()] + " " + localDate.getDate() + ", " + localDate.getFullYear());
		var date = new Date(localDate.valueOf() + localDate.getTimezoneOffset()*60000);

		// date = date.getFullYear() + "-" + 
		// 	("0" + (date.getMonth() + 1)).slice(-2) + "-" + 
		// 	("0" + date.getDate()).slice(-2) + "-" + 
		// 	("0" + date.getHours()).slice(-2) + "-" +
		// 	("0" + date.getMinutes()).slice(-2) + "-" + 
		// 	("0" + date.getSeconds()).slice(-2);
		loadTable(date);
	});
});