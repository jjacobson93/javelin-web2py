var currentDate = undefined;
var monthNames = [ "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December" ];

function setCurrentDate(date) {
	currentDate = date;
	var localDate = utcToLocal(date);
	$('.date-long-span').html(monthNames[localDate.getMonth()] + " " + localDate.getDate() + ", " + localDate.getFullYear());
}

function loadTable(section_id, date) {
	var date = dateToStartEnd(utcToLocal(date));
	$.ajax({
		type: "POST",
		url: "/studybuddies/table",
		data: {
			'section_id': section_id,
			'start': date.start,
			'end': date.end
		},
		success: function(content) {
			var v = $('#out-show-all-btn').attr('data-value');
			$('#sb-table-content').html(content);
			if (v == 'Show') {
				$('.sb-out-hide').hide();	
			}
			$('#sb-table-content').css("height", $(window).height()/2);
		}
	});
}

function loadSections(date) {
	var date = dateToStartEnd(utcToLocal(date));
	$.ajax({
		type: "POST",
		url: "/studybuddies/sections",
		data: {
			'start': date.start,
			'end': date.end
		},
		success: function(content) {
			window.history.pushState({"html":content, "pageTitle": "Javelin Study Buddies"},"", "");
			$('.sb-rows').html(content);
		}
	});
}

function loadCheckouts(date) {
	var date = dateToStartEnd(utcToLocal(date));
	$.ajax({
		type: "POST",
		url: "/studybuddies/checkout_table",
		data: {
			'start': date.start,
			'end': date.end
		},
		success: function(content) {
			$('#sb-table-content').html(content);
			$('#sb-table-content').css("height", $(window).height()/2);
		}
	});
}

function updateCounts() {
	var date = dateToStartEnd(utcToLocal($('#currdate-input').val()));
	$.ajax({
		type: "POST",
		url: "/studybuddies/call/json/counts",
		data: {
			'start': date.start,
			'end': date.end
		},
		dataType: 'json',
		success: function(data) {
			$.each(data, function(key, value) {
				$('#' + key + '_count').html((value != 0) ? value : '');
			});
		},
		error: function() {
			displayError("Could not update counts.");
		}
	});
}

function checkIn(person_id, section_id) {
	$.ajax({
		type: 'POST',
		url: '/studybuddies/call/json/checkin',
		data: {
			'person_id': person_id,
			'section_id': section_id
		},
		dataType: 'json',
		success: function() {
			$('#checkin_id_input').val('');
			$('#checkin_id_submit').addClass('disabled');
			var section_id = $('#sb_section_input').val();
			var date = $('#currdate-input').val();
			loadTable(section_id, date);
			updateCounts();
		},
		error: function() {
			displayError("Could not check in Student ID " + person_id + ".");
		}
	});
}

function checkOut(person_id, any) {
	$.ajax({
		type: 'POST',
		url: '/studybuddies/call/json/checkout',
		data: {
			'person_id': person_id
		},
		dataType: 'json',
		success: function() {
			if (!any) {
				$('#checkout_id_input').val('');
				$('#checkout_id_submit').addClass('disabled');
				var section_id = $('#sb_section_input').val();
				var date = $('#currdate-input').val();
				loadTable(section_id, date);
				updateCounts();
			} else {
				$('#checkoutall_id_input').val('');
				$('#checkoutall_id_submit').addClass('disabled');
				var date = $('#currdate-input').val();
				loadCheckouts(date);
			}
		},
		error: function() {
			displayError("Could not check in Student ID " + person_id + ".");
		}
	});
}

// function loadDates() {
// 	$.ajax({
// 		type: "POST",
// 		url: "/studybuddies/call/json/dates",
// 		dataType: 'json',
// 		success: function(data) {
// 			var list = $('<div/>');
// 			var d = $('#currdate-input').val();
// 			var currUtcDate = utcStringToDate(d);

// 			$.each(data, function(i, el) {
// 				var localDate = utcToLocal(data[i]);
// 				var utcDate = utcStringToDate(data[i]);

// 				var value = utcDate.getFullYear() + "-" + 
// 					("0" + (utcDate.getMonth() + 1)).slice(-2) + "-" + 
// 					("0" + utcDate.getDate()).slice(-2) + "-" + 
// 					("0" + utcDate.getHours()).slice(-2) + "-" +
// 					("0" + utcDate.getMinutes()).slice(-2) + "-" + 
// 					("0" + utcDate.getSeconds()).slice(-2);

// 				var label = monthNames[localDate.getMonth()] + " " + localDate.getDate() + ", " + localDate.getFullYear();

// 				list.append($('<li><a href="#" data-value="' + value +
// 					'">' + ((currUtcDate.getFullYear() == utcDate.getFullYear() && 
// 						currUtcDate.getMonth() == utcDate.getMonth() && currUtcDate.getDate() == utcDate.getDate()) ? '<i class="icon-caret-right"></i> ' : '') +
// 					label + '</a></li>'));
// 			});

// 			$('#currdate-input').val();
// 		},
// 		error: function() {
// 			$('#currdate-input').val()d-color: #f2dede; padding: 10px; text-align: center"><b>Error!</b></li>');
// 		}
// 	});
// }

$(function() {
	window.onpopstate = function(e){
		if (e.state){
			// document.getElementById("content").innerHTML = e.state.html;
			document.title = e.state.pageTitle;
		}
	};
	
	$('#checkin_id_submit').on('click', function() {
		var person_id = $('#checkin_id_input').val();
		var section_id = $('#sb_section_input').val();
		checkIn(person_id, section_id);
	});

	$('#checkout_id_submit').on('click', function() {
		var person_id = $('#checkout_id_input').val();
		checkOut(person_id, false);
	});

	$('#checkin_id_input').on('keyup', function(e) {
		var val = $(this).val();
		$('#checkin_id_submit').removeClass('disabled');
		if (val == '')
			$('#checkin_id_submit').addClass('disabled');

		if (e.keyCode == 13 && val != '')
			$("#checkin_id_submit").click();
	});

	$('#checkout_id_input').on('keyup', function(e) {
		var val = $(this).val();
		$('#checkout_id_submit').removeClass('disabled');
		if (val == '')
			$('#checkout_id_submit').addClass('disabled');

		if (e.keyCode == 13 && val != '')
			$("#checkout_id_submit").click();
	});

	$('#out-show-all-btn').on('click', function() {
		var v = $(this).attr('data-value');
		if (v == 'Show') {
			$(this).attr('data-value', 'Hide');
			$(this).html("Hide Inactive");
			$('.sb-out-hide').fadeIn(250);
			if ($('#sb-table-content table tbody tr:not(.sb-out-hide, #no-students-row)').length == 0) {
				$('#no-students-row').fadeOut(250);
			} else {
				$('#no-students-row').fadeIn(250);
			}
		}
		else {
			$(this).attr('data-value', 'Show');
			$(this).html("Show Inactive");
			$('.sb-out-hide').fadeOut(250);
			if ($('#sb-table-content table tbody tr:not(.sb-out-hide, #no-students-row)').length == 0) {
				$('#no-students-row').fadeIn(250);
			} else {
				$('#no-students-row').fadeOut(250);
			}
		}
	});

	$(document).on('click', 'button.sb-section', function() {
		var section = $(this).attr('data-section');
		var date = $('#currdate-input').val();
		var text = $(this).html();
		$('#section_title').html(text);
		$('#sb_section_input').val(section);

		loadTable(section, date);

		var pos = $(this).offset();
		var rowPos = $('.sb-rows').offset();
		var rowWidth = $('.sb-rows').width();
		var rowHeight = $('.sb-rows').height();
		$(".sb-main-view").offset(pos);
		$(".sb-main-view").css('display', 'block');
		$(".sb-main-view").css('width', $(this).outerWidth());
		$(".sb-main-view").css('height', $(this).outerHeight());
		$('.sb-rows').animate({
			opacity: 0
		}, 800);

		setTimeout(function() {
			$('.sb-rows').css('display', 'none');
		}, 850);

		$(".sb-main-view").animate({
			height: rowHeight,
			width: rowWidth,
			top: rowPos.top,
			left: rowPos.left,
			opacity: 1
		}, 800);

		setTimeout(function() {
			$(".sb-main-view").css('position', 'relative');
			$(".sb-main-view").css('top', 0);
			$(".sb-main-view").css('left', 0);
			$(".sb-main-view").css('width', '100%');
		}, 850);
	});

	$('#main-view-close').on('click', function() {
		$('.sb-main-view').animate({
			opacity: 0
		}, 300);

		setTimeout(function() {
			$(".sb-main-view").css('position', 'absolute');
			$(".sb-main-view").css('display', 'none');
			$('.sb-rows').css('display', 'block');
			$('.sb-rows').animate({
				opacity: 1
			}, 300);
			$('#section_title').html('');
		}, 400);

		setTimeout(function() {
			updateCounts();
		}, 450);
	});

	// $('#date-btn').on('click', function() {
	// 	$('#currdate-input').val()t-align: center'><span><i class='icon-spinner icon-spin icon-2x'></i></span></li>");
	// 	loadDates();
	// });

	// $('#currdate-input').val()i > a', function(e) {
	// 	e.preventDefault();
	// 	var value = $(this).attr('data-value');
	// 	var date = utcToLocal(value);
	// 	var label = monthNames[date.getMonth()] + " " + date.getDate() + ", " + date.getFullYear();
	// 	$('#currdate-input').val(), value);
	// 	$('#date-btn').html(label + " <span class='caret'></span>");
	// 	loadSections(value);
	// });

});