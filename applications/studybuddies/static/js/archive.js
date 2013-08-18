var currentDate = undefined;
var monthNames = [ "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December" ];

function setCurrentDate(date) {
	currentDate = date;
	var localDate = utcToLocal(date);
	$('.date-long-span').html(monthNames[localDate.getMonth()] + " " + localDate.getDate() + ", " + localDate.getFullYear());
}

function loadTable(date) {
	console.log("LOADING TABLE WITH DATE: " + date);
	var local = utcToLocal(date);
	console.log("LOCAL: " + local);
	var date = dateToStartEnd(local);
	console.log("DATE START/END: (" + date.start + ", " + date.end + ")");
	$.ajax({
		type: "POST",
		url: "/studybuddies/archive/table",
		data: {
			'start': date.start,
			'end': date.end
		},
		success: function(content) {
			window.history.pushState({"html":content, "pageTitle": "Javelin Study Buddies"},"", "");
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

	$("#date-btn").datetimepicker({
		format: 'yyyy-mm-dd-hh-ii-ss',
		showMeridian: true,
        autoclose: true,
        todayBtn: true,
        minView: 2
	}).on('changeDate', function(ev){
		console.log("DATE CHANGED: " + ev.date);
		console.log("TIMEZONE OFFSET: " + ev.date.getTimezoneOffset());
		var localDate = new Date(ev.date.valueOf() + ev.date.getTimezoneOffset()*60000);
		console.log("LOCAL DATE: " + localDate);
		$('.date-long-span').html(monthNames[localDate.getMonth()] + " " + localDate.getDate() + ", " + localDate.getFullYear());
		var date = new Date(localDate.valueOf() + localDate.getTimezoneOffset()*60000);
		console.log("UTC DATE: " + date);

		date = date.getFullYear() + "-" + 
			("0" + (date.getMonth() + 1)).slice(-2) + "-" + 
			("0" + date.getDate()).slice(-2) + "-" + 
			("0" + date.getHours()).slice(-2) + "-" +
			("0" + date.getMinutes()).slice(-2) + "-" + 
			("0" + date.getSeconds()).slice(-2);
		loadTable(date);
	});

	// $('#date-btn').on('click', function() {
	// 	$('#date-menu').html("<li style='text-align: center'><span><i class='icon-spinner icon-spin icon-2x'></i></span></li>");
	// 	loadDates();
	// });

	// $('#date-menu').on('click', 'li > a', function(e) {
	// 	e.preventDefault();
	// 	$('#date-menu').attr('data-value', $(this).attr('data-value'));
	// 	$('#date-btn').html($(this).html() + " <span class='caret'></span>");
	// 	loadTable($(this).attr('data-value'));
	// });
});