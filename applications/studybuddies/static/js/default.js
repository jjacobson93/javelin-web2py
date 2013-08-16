function loadTable(section_id, date) {
	$.ajax({
		type: "POST",
		url: "/table",
		data: {
			'section_id': section_id,
			'date': date
		},
		success: function(content) {
			$('#sb-table-content').html(content);
			$('#sb-table-content').css("height", $(window).height()/2);
		}
	});
}

function loadSections(date) {
	$.ajax({
		type: "POST",
		url: "/sections",
		data: {
			'date': date
		},
		success: function(content) {
			window.history.pushState({"html":content, "pageTitle": "Javelin Study Buddies"},"", "/?date=" + date);
			$('.sb-rows').html(content);
		}
	});
}

function reloadTable() {
	var section_id = $('#sb_section_input').val();
	var date = $('#date-menu').attr("data-value");
	$.ajax({
		type: "POST",
		url: "/table",
		data: {
			'section_id': section_id,
			'date': date
		},
		success: function(content) {
			var v = $('#out-show-all-btn').attr('data-value');
			$('#sb-table-content').html(content);
			if (v == 'Show') {
				$('.sb-out-hide').hide();	
			}
		}
	});
}

function updateCounts() {
	var date = $('#date-menu').attr("data-value");
	$.ajax({
		type: "POST",
		url: "/call/json/counts",
		data: {
			'date': date
		},
		dataType: 'json',
		success: function(data) {
			$.each(data, function(key, value) {
				console.log($('#' + key + '_count'));
				$('#' + key + '_count').html((value != 0) ? value : '');
			});
		},
		error: function() {
			displayError("Could not update counts.");
		}
	});
}

function checkIn(person_id, section_id) {
	var date = $('#date-menu').attr("data-value");
	$.ajax({
		type: 'POST',
		url: '/call/json/checkin',
		data: {
			'person_id': person_id,
			'section_id': section_id,
			'date': date
		},
		dataType: 'json',
		success: function() {
			$('#checkin_id_input').val('');
			$('#checkin_id_submit').addClass('disabled');
			reloadTable();
			updateCounts();
		},
		error: function() {
			displayError("Could not check in Student ID " + person_id + ".");
		}
	});
}

function checkOut(person_id, section_id) {
	var date = $('#date-menu').attr("data-value");
	$.ajax({
		type: 'POST',
		url: '/call/json/checkout',
		data: {
			'person_id': person_id,
			'section_id': section_id,
			'date': date
		},
		dataType: 'json',
		success: function() {
			$('#checkout_id_input').val('');
			$('#checkout_id_submit').addClass('disabled');
			reloadTable();
			updateCounts();
		},
		error: function() {
			displayError("Could not check in Student ID " + person_id + ".");
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
		}
	};
	
	$('#checkin_id_submit').on('click', function() {
		var person_id = $('#checkin_id_input').val();
		var section_id = $('#sb_section_input').val();
		checkIn(person_id, section_id);
	});

	$('#checkout_id_submit').on('click', function() {
		var person_id = $('#checkout_id_input').val();
		var section_id = $('#sb_section_input').val();
		checkOut(person_id, section_id);
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
			$('.sb-out-hide').fadeIn(500);
			$('#no-students-row').hide();
		}
		else {
			$(this).attr('data-value', 'Show');
			$(this).html("Show Inactive");
			$('.sb-out-hide').fadeOut(500);

			if ($('#sb-table-content table tbody tr:not(.sb-out-hide, #no-students-row)').length == 0) {
				$('#no-students-row').fadeIn(500);;
			} else {
				$('#no-students-row').fadeOut(500);
			}
		}
	});

	$(document).on('click', 'button.sb-section', function() {
		var section = $(this).attr('data-section');
		var date = $('#date-menu').attr('data-value');
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

	$('#date-btn').on('click', function() {
		$('#date-menu').html("<li style='text-align: center'><span><i class='icon-spinner icon-spin icon-2x'></i></span></li>");
		loadDates();
	});

	$('#date-menu').on('click', 'li > a', function(e) {
		e.preventDefault();
		$('#date-menu').attr('data-value', $(this).attr('data-value'));
		$('#date-btn').html($(this).html() + " <span class='caret'></span>");
		loadSections($(this).attr('data-value'));
	});

});