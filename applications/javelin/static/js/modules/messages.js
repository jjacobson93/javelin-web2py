$(function() {
	$('#to_select').select2({
		placeholder: "To",
		id: function(person) {
			return person['id'];
		},
		ajax: {
			type: 'POST',
			url: '/people/call/json/leaders',
			dataType: 'json',
			quietMillis: 100,
			data: function(term, page) {
				return { query: term };
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