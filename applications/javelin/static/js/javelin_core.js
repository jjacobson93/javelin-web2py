function displaySuccess(message) {
	$('#success-alert').html("<strong>Saved!</strong> " + message)
	$('#success-alert').css('display', 'block');
	setTimeout(function() {
		$("#success-alert").fadeTo(500, 0).slideUp(500, function(){
			$('#success-alert').css('display', 'none');
			$('#success-alert').css('opacity', '');
		});
	}, 5000);
}

function displayError(message) {
	$('#error-alert').html("<strong>Error!</strong> " + message)
	$('#error-alert').slideDown(100, function() {
		$('#error-alert').css('display', 'block');
	});
	setTimeout(function() {
		$("#error-alert").fadeTo(500, 0).slideUp(500, function(){
			$('#error-alert').css('display', 'none');
			$('#error-alert').css('opacity', '');
		});
	}, 5000);
}