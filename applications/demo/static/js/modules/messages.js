$(function() {
	$('#to_select').select2({
		placeholder: "To",
		id: function(record) {
			return record['id'];
		},
		ajax: {
			type: 'POST',
			url: '/demo/messages/call/json/get_recipients',
			dataType: 'json',
			quietMillis: 100,
			data: function(term, page) {
				return { query: term };
			},
			results: function(data, page) {
				return { results: data };
			}
		},
		formatResult: function(record, container, query, escapeMarkup) {
			var markup=[]; 

			if (!record['text']) {
				if (record['first_name'])
					window.Select2.util.markMatch(record['last_name'] + ', ' + record['first_name'], query.term, markup, escapeMarkup); 
				else
					window.Select2.util.markMatch(record['last_name'], query.term, markup, escapeMarkup); 
			} else {
				window.Select2.util.markMatch(record['text'], query.term, markup, escapeMarkup); ;
			}

			return markup.join("")
		},
		formatSelection: function(record) {
			if (!record['text']) {
				if (record['first_name']) 
					return record['last_name'] + ', ' + record['first_name'];
				else
					return record['last_name'];
			} else {
				return record['text'];
			}
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
			url: '/demo/messages/call/json/send_sms',
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