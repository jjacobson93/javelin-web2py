function loadTable(date) {
	$.ajax({
		type: "POST",
		url: "/archive/table",
		data: {
			'date': date
		},
		success: function(content) {
			window.history.pushState({"html":content, "pageTitle": "Javelin Study Buddies", "date": date},"", "/archive?date=" + date);
			$('#sb-table-content').html(content);
			$('#sb-table-content').css("height", $(window).height() - $('.navbar').outerHeight() - 100);
		}
	});
}

function loadDates() {
	$.ajax({
		type: "POST",
		url: "/call/json/dates",
		dataType: 'json',
		success: function(data) {
			var list = $('<div/>');
			var d = $('#date-menu').attr('data-value');

			$.each(data, function(i, el) {
				list.append($('<li><a href="#" data-value="' + data[i]['value'] +
					'">' + ((d == data[i]['value']) ? '<i class="icon-caret-right"></i> ' : '') +
					data[i]['label'] + '</a></li>'));
			});

			$('#date-menu').html(list.html());
		},
		error: function() {
			displayError("Could not load date menu.");
			$('#date-menu').append('<li style="background-color: #f2dede; padding: 10px; text-align: center"><b>Error!</b></li>');
		}
	});
}

$(function() {
	window.onpopstate = function(e){
		if (e.state){
			document.getElementById("content").innerHTML = e.state.html;
			document.title = e.state.pageTitle;
			loadTable(e.state.date);
		}
	};

	$('#sb-table-content').css("height", $(window).height() - $('.navbar').outerHeight() - 100);

	$('#date-btn').on('click', function() {
		$('#date-menu').html("<li style='text-align: center'><span><i class='icon-spinner icon-spin icon-2x'></i></span></li>");
		loadDates();
	});

	$('#date-menu').on('click', 'li > a', function(e) {
		e.preventDefault();
		$('#date-menu').attr('data-value', $(this).attr('data-value'));
		$('#date-btn').html($(this).html() + " <span class='caret'></span>");
		loadTable($(this).attr('data-value'));
	});
});