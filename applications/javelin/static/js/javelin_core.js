$(function() {
	$('a.btn').on('click', function(e) {
		if ($(this).attr('href') === "#")
			e.preventDefault();
	});

	$('a, btn').on('click', function(e) {
		if($(this).hasClass('disabled')) {
			 e.preventDefault();
			 return false;
		}
	});
});

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