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