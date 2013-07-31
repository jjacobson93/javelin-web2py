$(function() {
	$('#to_select').select2();

	$('#message').on('keyup', function() {
		var count = $(this).val().length;
		$('#char-count').html(count);

		$('#send-btn').removeClass('disabled');
		if (count == 0) {
			$('#send-btn').addClass('disabled');
		}
	});

	$('#send-btn').on('click', function() {
		$('#send-btn').button('loading');
		var to = $('#to_select').val();
		var message = $('#message').val();

		$.ajax({
			type: 'POST',
			url: '/messages/call/json/send_sms',
			data: {
				'message': message,
				'to': to
			},
			dataType: 'json',
			success: function() {
				$('#message').val('');
				$('#char-count').html(0);
				$('#send-btn').button('reset');
				displaySuccess("Message will be sending momentarily.");
			},
			error: function() {
				displayError("Message could not be sent");
			}
		});
	});
});