var columns = ['id', 'leaders', 'score'];

function reloadLiveTable() {
	$.ajax({
		type: 'GET',
		url: '/scores/call/json/data',
		dataType: 'json',
		cache: false,
		success: function(data) {
			$.each(data, function(i,e) {
				var allSame = true;
				var oldRow = $('tr[data-id="' + e.id + '"]');

				if (oldRow.length) {
					var cells = oldRow.find('td');
					$.each(columns, function(j, col) {
						var oldD = $(oldRow).find('td').eq(j).attr('data-attr');
						var newD = e[col];
						if (allSame && oldD != newD) {
							allSame = false;
						}
					});

					if (!allSame) {
						var row_type = '';
						if (e.score == 'A') { row_type = 'success'; data_value = 3; }
						else if (e.score == 'I') { row_type = 'warning'; data_value = 2; }
						else if (e.score == 'M') { row_type = 'error'; data_value = 1; }
						else { data_value = -1; }
						var row = $('<tr class="' + row_type + '" data-id="' + e.id + '">' +
						'	<td data-attr="' + e.id + '">' + e.id + '</td>' +
						'	<td data-attr="'+ e.leaders + '"><small>'+ e.leaders + '</small></td>' +
						'	<td data-attr="' + e.score + '" data-value="' + data_value + '">' +
						'		<div class="fuelux">' +
						'			<div class="select btn-group" id="aim_select_' + e.id +'">' + 
						'				<button type="button" data-toggle="dropdown" class="btn dropdown-toggle"><span class="dropdown-label"></span><span class="caret"></span></button>' +
						'				<ul class="dropdown-menu" style="min-width: 50px;">' + 
						'					<li data-value="None" ' + ((e.score=='None') ? 'data-selected=true' : '') + '><a href="#">None</a></li>' +
						'					<li data-value="A" ' + ((e.score=='A') ? 'data-selected=true' : '') + '><a href="#">A</a></li>' +
						'					<li data-value="I" ' + ((e.score=='I') ? 'data-selected=true' : '') + '><a href="#">I</a></li>' +
						'					<li data-value="M" ' + ((e.score=='M') ? 'data-selected=true' : '') + '><a href="#">M</a></li>' +
						'				</ul>' +
						'			</div>' + 
						'		</div>' +
						'</tr>');
						oldRow.replaceWith(row);
					}
				} else {
					// console.log('No old row for ' + e.id);
					var row_type = '';
					if (e.score == 'A') { row_type = 'success'; data_value = 3; }
					else if (e.score == 'I') { row_type = 'warning'; data_value = 2; }
					else if (e.score == 'M') { row_type = 'error'; data_value = 1; }
					else { data_value = -1; }

					var row = $('<tr class="' + row_type + '" data-id="' + e.id + '">' +
						'	<td data-attr="' + e.id + '">' + e.id + '</td>' +
						'	<td data-attr="'+ e.leaders + '"><small>'+ e.leaders + '</small></td>' +
						'	<td data-attr="' + e.score + '" data-value="' + data_value + '">' +
						'		<div class="fuelux">' +
						'			<div class="select btn-group" id="aim_select_' + e.id +'">' + 
						'				<button type="button" data-toggle="dropdown" class="btn dropdown-toggle"><span class="dropdown-label"></span><span class="caret"></span></button>' +
						'				<ul class="dropdown-menu" style="min-width: 50px;">' + 
						'					<li data-value="None" ' + ((e.score=='None') ? 'data-selected=true' : '') + '><a href="#">None</a></li>' +
						'					<li data-value="A" ' + ((e.score=='A') ? 'data-selected=true' : '') + '><a href="#">A</a></li>' +
						'					<li data-value="I" ' + ((e.score=='I') ? 'data-selected=true' : '') + '><a href="#">I</a></li>' +
						'					<li data-value="M" ' + ((e.score=='M') ? 'data-selected=true' : '') + '><a href="#">M</a></li>' +
						'				</ul>' +
						'			</div>' + 
						'		</div>' +
						'</tr>');
					$('table tbody').append(row);
				}

				$('.fuelux .select[id^="aim_select"]').each(function(i, e) {
					var val = $(this).parent().parent().attr('data-attr');
					$(this).select('selectByValue', val);
				});
			});
		},
		error: function(e, ts) {
			console.log('Could not get data');
			// console.log(e);
		}
	});
}

function updateAIM(id, aim) {
	$.ajax({
		type: 'POST',
		url: '/scores/call/json/update_score',
		data: {
			'id': id,
			'score': aim
		},
		dataType: 'json'
	});
}

$(function() {
	$('.fuelux .select[id^="aim_select"]').each(function(i, e) {
		var val = $(this).find('li[data-selected=true]:first').attr('data-value');
		$(this).select();
		$(this).select('selectByValue', val);
	});

	// $('.fuelux .select[id^="aim_select"]').on('click', function() {
	// 	console.log('clicked');
	// });

	$('.fuelux .select[id^="aim_select"]').on('changed', function(event, data) {
		var cell = $(this).parent().parent();
		var row = cell.parent();
		var id = $(row).attr('data-id');
		var aim = (data.value=='None') ? null : data.value;
		row.removeAttr('class');
		if (data.value == 'A') {
			row.addClass('success');
			cell.attr('data-value', '3');
		} else if (data.value == 'I') {
			row.addClass('info');
			cell.attr('data-value', '2');
		} else if (data.value == 'M') {
			row.addClass('error');
			cell.attr('data-value', '1');
		} else {
			cell.attr('data-value', '-1');
		}
		updateAIM(id, aim);
	});

	setInterval(function() {
		var open = $('.open');
		if (!open.length)
			reloadLiveTable();
	}, 4000);
});