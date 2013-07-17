$(function() {
	$('#save-button').on('click', function(e) {
		e.preventDefault();
		var data = [];
		$('#modules-tbody').find('tr').each(function() {
			var name = $(this).find('td').eq(0).html();
			var value = $(this).find('input').val();
			if (value !== "")
				data.push({'name' : name.toLowerCase(), 'value' : value});
		});

		if (data.length > 0) {
			$.ajax({
				type: 'POST',
				url: '/jadmin/call/json/update_names',
				data: 'names=' + JSON.stringify(data),
				dataType: 'json',
				success: function() {
					$('#success-alert').html("<strong>Saved!</strong> The changes were saved.")
					$('#success-alert').css('display', 'block');
					setTimeout(function() {
						$("#success-alert").fadeTo(500, 0).slideUp(500, function(){
							$('#success-alert').css('display', 'none');
							$('#success-alert').css('opacity', '');
							location.reload();
						});
					}, 1000);
				},
				error: function() {
					$('#error-alert').html("<strong>Error!</strong> The changes could not be saved")
					$('#error-alert').css('display', 'block');
					setTimeout(function() {
						$("#error-alert").fadeTo(500, 0).slideUp(500, function(){
							$('#error-alert').css('display', 'none');
							$('#error-alert').css('opacity', '');
						});
					}, 5000);
				}
			});
		}
	});

	$('#add-user-button').on('click', function(e) {
		e.preventDefault();
		$('#add-user-modal').modal('show');
	});
});