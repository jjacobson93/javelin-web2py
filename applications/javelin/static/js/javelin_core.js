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

	$('.mainnav-collapse').overflowNavs({
		"more" : "More",
		"offset" : "325"
	});

	$(window).on('resize', function() {
		if ($(window).width() > 780) {
			$('.mainnav-collapse').overflowNavs({
				"more" : "More",
				"offset" : "325"
			});
		} else {
			$('.mainnav-collapse').overflowNavs("destroy");
		}
	});
});

function displayFlash(message) {
	if (message != '') {
		$('#response_flash').html(message);
		$("#flash_alert").css('display', 'block');
		setTimeout(function() {
			$("#flash_alert").fadeTo(500, 0).slideUp(500, function(){
				$("#flash_alert").css('display', 'none');
				$("#flash_alert").css('opacity', '');
			});
		}, 5000);
	}
}

function displaySuccess(message, inModal) {
	var id = (inModal) ? "success-alert-modal" : "success-alert";

	$("#" + id).remove();

	var alert = $('<div/>', { 
		class: "alert alert-success alert-dismissable fade in", 
		id: id,
		style: "display: none"
	}).append($('<span/>')).append('<strong>Success!</strong> ' + message);

	alert.prepend('<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>');

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
		class: "alert alert-danger alert-dismissable fade in", 
		id: id,
		style: "display: none"
	}).append($('<span/>')).append('<strong>Error!</strong> ' + message);

	alert.prepend('<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>');

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