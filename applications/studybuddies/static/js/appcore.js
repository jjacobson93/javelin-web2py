function dateToStartEnd(date) {
	return {
		start: dateToStringValue(new Date(date.getFullYear(), date.getMonth(), date.getDate())),
		end: dateToStringValue(new Date(date.getFullYear(), date.getMonth(), date.getDate() + 1))
	};
}

function utcToLocal(dateString) {
	var tmpDate = utcStringToDate(dateString); //UTC time
	var tzOffset = new Date().getTimezoneOffset();
	return new Date(tmpDate.valueOf() - tzOffset*60000);
}

function utcStringToDate(dateString) {
	var date = dateString.split('-');
	return new Date(date[0], date[1] - 1, date[2], date[3], date[4], date[5]);
}

function dateToStringValue(date) {
	date = shiftToUTC(date);
	return date.getFullYear() + "-" + 
		("0" + (date.getMonth() + 1)).slice(-2) + "-" + 
		("0" + date.getDate()).slice(-2) + "-" + 
		("0" + date.getHours()).slice(-2) + "-" +
		("0" + date.getMinutes()).slice(-2) + "-" + 
		("0" + date.getSeconds()).slice(-2);
}

function shiftToUTC(date) {
	var tzOffset = new Date().getTimezoneOffset();
	return new Date(date.valueOf() + tzOffset*60000);
}

function formatAMPM(date) {
	if (date) {
		var hours = date.getHours();
		var minutes = date.getMinutes();
		var ampm = hours >= 12 ? 'PM' : 'AM';
		hours = hours % 12;
		hours = hours ? hours : 12; // the hour '0' should be '12'
		minutes = minutes < 10 ? '0'+minutes : minutes;
		var strTime = hours + ':' + minutes + ' ' + ampm;
		return strTime;
	} else
		return "None"
}

// function checkIn(id) {
// 	$.ajax({
// 		type: 'POST',
// 		url: '/checkin/call/json/check',
// 		data: {
// 			'id': id
// 		},
// 		dataType: 'json',
// 		success: function() {
// 			$('#checkin_id_input').val('');
// 			reloadTable();
// 		},
// 		error: function() {
// 			displayError("Could not check in Student ID " + id + ".");
// 		}
// 	});
// }

// function checkOut(id) {
// 	$.ajax({
// 		type: 'POST',
// 		url: '/checkout/call/json/check',
// 		data: {
// 			'id': id
// 		},
// 		dataType: 'json',
// 		success: function() {
// 			$('#checkout_id_input').val('');
// 			reloadTable();
// 		},
// 		error: function() {
// 			displayError("Could not check in Student ID " + id + ".");
// 		}
// 	});
// }

function displaySuccess(message, inModal) {
	var id = (inModal) ? "success-alert-modal" : "success-alert";

	$("#" + id).remove();

	var alert = $('<div/>', { 
		class: "alert alert-success", 
		id: id,
		style: "display: none"
	}).append($('<span/>')).append('<strong>Success!</strong> ' + message);

	if (inModal) {
		$('div.modal[aria-hidden=false] .modal-body').prepend(alert);
	} else {
		$('div.alert-container').append(alert);
	}

	$("#" + id).slideDown(100, function() {
		$("#" + id).css('display', 'block');
	});

	setTimeout(function() {
		$("#" + id).fadeTo(500, 0).slideUp(500, function(){
			$("#" + id).css('display', 'none');
			$("#" + id).css('opacity', '');
		});
	}, 5000);
}

function displayError(message, inModal) {
	var id = (inModal) ? "error-alert-modal" : "error-alert";

	$("#" + id).remove();

	var alert = $('<div/>', { 
		class: "alert alert-danger", 
		id: id,
		style: "display: none"
	}).append($('<span/>')).append('<strong>Error!</strong> ' + message);

	if (inModal) {
		$('div.modal[aria-hidden=false] .modal-body').prepend(alert);
	} else {
		$('div.alert-container').append(alert);
	}

	$("#" + id).slideDown(100, function() {
		$("#" + id).css('display', 'block');
	});

	setTimeout(function() {
		$("#" + id).fadeTo(500, 0).slideUp(500, function(){
			$("#" + id).css('display', 'none');
			$("#" + id).css('opacity', '');
		});
	}, 5000);
}

function displayFlash(msg) {
	if (msg != '') {
		$('#response_flash').html(msg);
		$("#flash_alert").css('display', 'block');
		setTimeout(function() {
			$("#flash_alert").fadeTo(500, 0).slideUp(500, function(){
				$("#flash_alert").css('display', 'none');
				$("#flash_alert").css('opacity', '');
			});
		}, 5000);
	}
}

$(function() {
	$('a, a.btn').on('click', function(e) {
		if ($(this).attr('href') === "#")
			e.preventDefault();

		if ($(this).hasClass('disabled')) {
			e.preventDefault();
			return false;
		}
	});

	$(".alert").alert();
});