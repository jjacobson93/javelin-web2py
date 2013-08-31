var tableIsInit = false;

function loadRecord(id) {
	$.ajax({
		type: "POST",
		url: "/people/call/json/record",
		data: {
			'id' : id
		},
		dataType: "json",
		success: function(data) {
			$.each(data, function(k, v) {
				if (k != 'pic')
					if (v && typeof(v) != "boolean")
						$('#' + k).val(String(v));
					else if (typeof(v) == "boolean")
						$('#' + k).prop('checked', v);
					else
						$('#' + k).val("");
			});

			// var pic = data['pic']
			// $('#person-pic').empty();
			// if (pic != null) {
			// 	var img = new Image();
			// 	var imgElement = $("<img src='data:image/jpeg;base64," + pic + "'>");
			// 	$('#person-pic').css("padding", 0);
			// 	$('#person-pic').append(imgElement);
			// } else {
			// 	$('#person-pic').text("No picture");
			// }
		},
		error: function() {
			displayError("The record could not be loaded")
			// $('#person-pic').empty();
			// $('#person-pic').text("No picture");
		}
	});

	loadSchedule(id);
}

function loadSchedule(id) {
	$.ajax({
		type: 'POST',
		url: '/people/call/json/schedule',
		data: {
			'id': id
		},
		dataType: 'json',
		success: function(data) {
			var tbody = $('<tbody/>');
			$.each(data, function(i,row) {
				tbody.append($('<tr><td>' + row.course.period + '</td>' + 
				'<td>' + row.course.title + '</td>' +
				'<td>' + row.teacher.teacher_name + '</td></tr>'));
			});
			$('#schedule-table tbody').replaceWith(tbody);
		},
		error: function() {
			displayError('Could not load student schedule.');
		}
	});
}

function saveChanges(toPrev) {
	var id;
	var values = {};
	$('#main-form input, #main-form select, #notestab textarea').each(function(i, e) {
		var eid = $(e).attr('id');
		if ($(e).attr('type') == 'checkbox')
			values[eid] = $(e).prop('checked');
		else if ($(e).val() != "" && eid != 'id')
			values[eid] = $(e).val();
		else if (eid == "id")
			id = $(e).val();
		else if ($(e).val() == "" || $(e).val() == null)
			values[eid] = null;
	});

	$.ajax({
		type: "POST",
		url: "/people/call/json/update_record",
		data: {
			'id' : id,
			'values' : JSON.stringify(values)
		},
		dataType: "json",
		success: function() {
			saveComplete(true, toPrev);
			displaySuccess("The record has been saved.");
		},
		error: function() {
			saveComplete(false, toPrev);
			displayError("The record could not be saved.");
		}
	});

}

function saveComplete(saved, toPrev) {
	$('#save-approve-modal').modal('hide');
	
	if (saved && !toPrev) {
		$('#save-button').addClass('disabled');
	} else if (saved && toPrev) {
		$('#save-button').addClass('disabled');
		$('#main-container').carousel('prev');
	}
}

function updatePic(id, pic) {
	$.ajax({
		type: "POST",
		url: "/people/call/json/update_pic",
		data: {
			"id" : id,
			"pic" : pic
		},
		dataType: 'json',
		success: function() {
			loadRecord(id);
			$('.fileupload').fileupload('clear');
			displaySuccess("The picture has been uploaded.");
		},
		error: function() {
			displayError("The picture could not be uploaded.");
		}
	});
}

function checkPictureForUpload() {
	if ($('#current-pic').html() !== '') {
		$('#upload-pic-btn').removeClass('disabled');
	} else if (!$('#upload-pic-btn').hasClass('disabled')) {
		$('#upload-pic-btn').addClass('disabled');
	}
}

$(function() {
	// $.fn.dataTableExt.afnFiltering.push(
	// 	function( oSettings, aData, iDataIndex ) {
	// 		var value = $('.fuelux .select.filter').select('selectedItem').value;
	// 		switch(value) {
	// 			case 'leaders':
	// 				if(aData[5] && aData[5] != 9 && aData[7]) return true;
	// 				else return false;
	// 				break;
	// 			case 'freshmen':
	// 				if(aData[5] && aData[5] == 9) return true;
	// 				else return false;
	// 				break;
	// 			case 'non_leaders':
	// 				if(aData[5] && aData[5] != 9 && !aData[7]) return true;
	// 				else return false;
	// 				break;
	// 			default:
	// 				return true;
	// 				break;
	// 		}
	// 	}
	// );

	var peopleTable = $('#people-table').jTable({
		columns: [
			{
				'key': 'id',
				'label': 'ID'
			},
			{
				'key': 'student_id',
				'label': 'Student ID'
			},
			{ 
				'key': 'last_name',
				'label': 'Last Name',
			},
			{ 
				'key': 'first_name',
				'label': 'First Name',
			},
			{
				'key': 'grade',
				'label': 'Grade'
			}
		],
		ajax: {
			source: '/people/call/json/data',
			error: function() {
				displayError("Could not load data");
			}
		},
		title: 'People',
		pageSize: 100,
		filter: {
			fn: function(value, data) {
				return _.filter(data, function (item) {
					switch(value) {
						case 'leaders':
							if(item.grade != 9 && item.leader) return true;
							break;
						case 'freshmen':
							if(item.grade == 9) return true;
							break;
						case 'non_leaders':
							if(item.grade != 9 && !item.leader) return true;
							break;
						default:
							return true;
							break;
					}
				});
			},
			options: [
				{'value': 'all','label': 'All'},
				{'value': 'leaders','label': 'Leaders'},
				{'value': 'freshmen','label': 'Freshmen'},
				{'value': 'non_leaders','label': 'Neither'}
			],
			class: 'select2'
		}
	});

	// $('.select2').select2();
	// $('.select2').css('margin', '-10px 0 0');

	// $('.table-header').css({
	// 	'display': 'inline',
	// 	'margin-right' : '10px',
	// 	'font-weight': 'bold',
	// 	'font-size': '26px'
	// });

	// $('.fuelux .select').append("<div class='btn-group' style='margin-bottom: 8px'><button type='button' data-toggle='dropdown' class='btn btn-default dropdown-toggle' style='margin-top: -8px'>" +
	// 	"<span class='dropdown-label'></span><span class='caret'></span></button>" + 
	// 	"<ul class='dropdown-menu' role='menu'>" +
	// 	"<li data-value='all'><a href='#'>All</a></li>" + 
	// 	"<li data-value='freshmen'><a href='#'>Freshmen</a></li>" +
	// 	"<li data-value='leaders'><a href='#'>Leaders</a></li>" + 
	// 	"<li data-value='non_leaders'><a href='#'>Non-Leaders</a></li></ul></div>");

	// $('.fuelux .select').each(function() {
	// 	var $this = $(this);
	// 	if ($this.data('select')) return;
	// 		$this.select($this.data());

	// 	$(this).on('changed', function() {
	// 		peopleTable.fnDraw();
	// 	});
	// });

	$('#person-pane').on('change', 'input', function() {
		$('#save-button').removeClass('disabled');
	});

	$('#person-pane').on('keyup', 'input,textarea', function() {
		$('#save-button').removeClass('disabled');
	});

	$('#person-pane').on('change', 'select', function() {
		$('#save-button').removeClass('disabled');
	});

	$(document).on('mouseleave', '.carousel', function() {
		$(this).carousel('pause');
	});

	$('.table > tbody').on('click', 'tr', function() {
		// row was clicked
		if ($(this).find("td").html() !== "0 items") {
			var td = $(this).find("td");
			var p_id = td.eq(0).html();
			
			loadRecord(p_id);
			
			$('#main-container').carousel('next');
			$('#main-container').carousel('pause');
		}
	});

	$('a').on('click', function(e) {
		if($(this).hasClass('disabled')) {
			 e.preventDefault();
			 return false;
		}
	});

	$('#main-container').on('slid', function() {
		// $('.carousel-inner').css('overflow', 'visible');
		$('#prev-button').removeClass('disabled');
		$('#add-button').removeClass('disabled');
		
		if ($('.carousel-inner .item:first').hasClass('active')) {
			$('#prev-button').addClass('disabled');
			peopleTable.jTable('seamlessReload');
		} 
		else if ($('.carousel-inner .item:last').hasClass('active')) {
			$('#add-button').addClass('disabled');
		}
	});

	$('#main-container').on('slide', function() {
		// $('.carousel-inner').css('overflow', 'hidden');
	});

	$('#save-button').on('click', function(e) {
		e.preventDefault();
		var btn = $(this);
		if (!btn.hasClass("disabled")) {
			btn.button('loading');
			saveChanges(false);
			btn.button('reset');
		}
	});

	$('#prev-button').on('click', function(e) {
		if($(this).hasClass('disabled')) {
			 e.preventDefault();
			 return false;
		}

		if (!$('#save-button').hasClass('disabled')) {
			$('#save-approve-modal').modal('show');
		} else {
			$('#main-container').carousel('prev');
		}
	});

	$('#cont-button').on('click', function(e) {
		e.preventDefault();
		$('#save-button').addClass('disabled');
		$('#main-container').carousel('prev');
	});

	$('#save-changes-button').on('click', function(e) {
		e.preventDefault();
		saveChanges(true);
	});

	$('#person-pic').on('click', function(e) {
		e.preventDefault();
		$('#current-pic').empty();
		$('#current-pic').append($('#person-pic').html());
		$('#current-pic').css("padding", 0);

		$('#upload-pic-modal').modal('show');
	});

	$('#upload-pic-btn').on('click', function(e) {
		e.preventDefault();
		var id = $('#id').val();
		var pic = $('#current-pic').find("img").attr("src");
		pic = pic.substr(pic.indexOf(",") + 1);

		$('#upload-pic-modal').modal('hide');

		updatePic(id, pic);
	})

	$('#upload-btn').on('click', function(e) {
		e.preventDefault();
		$('#upload-doc-modal').modal({
			show: true,
			keyboard: true
		});
	});

	$('#remove-btn').on('click', function(e) {
		e.preventDefault();
		// $('.fileupload').fileupload('clear');
		// $('#current-pic').empty();
		// $('#current-pic').append($('#person-pic').html());
	});

	$('.fileupload').on('change', function(e) {
		checkPictureForUpload();
	});

	$('#upload-pic-modal').on('hidden', function() {
		$('.fileupload').fileupload('clear');
		$('.fileupload').fileupload('reset');
		if (!$('#upload-pic-btn').hasClass('disabled')) {
			$('#upload-pic-btn').addClass('disabled');
		}
	});
});