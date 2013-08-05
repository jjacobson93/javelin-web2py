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

			var pic = data['pic']
			$('#person-pic').empty();
			if (pic != null) {
				var img = new Image();
				var imgElement = $("<img src='data:image/jpeg;base64," + pic + "'>");
				$('#person-pic').css("padding", 0);
				$('#person-pic').append(imgElement);
			} else {
				$('#person-pic').text("No picture");
			}
		},
		error: function() {
			displayError("The record could not be loaded")
			$('#person-pic').empty();
			$('#person-pic').text("No picture");
		}
	});
}

function saveChanges(toPrev) {
	var id;
	var values = {};
	$('#main-form input, #main-form select').each(function(i, e) {
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
	$('#people-table').datagrid({
		dataSource: new PeopleDataSource({
			columns: [
				{
					property: 'id',
					label: 'ID',
					sortable: true
				},
				{
					property: 'student_id',
					label: 'Student ID',
					sortable: true
				},
				{
					property: 'last_name',
					label: 'Last Name',
					sortable: true
				},
				{
					property: 'first_name',
					label: 'First Name',
					sortable: true
				},
				{
					property: 'gender',
					label: 'Gender',
					sortable: true
				},
				{
					property: 'crew',
					label: 'Crew',
					sortable: true
				}
			]
		}),
		stretchHeight: true
	});

	$('#people-table').on('loaded', function() {
		if (!tableIsInit) {
			tableIsInit = true;
			$('#people-pagesize').select2();
			$('#people-page-select').select2({placeholder: "1"});
		}
	});

	$('#people-div').height($(window).height()*.6);

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

	$(window).on('resize', function() {
		if ($(window).width() < 1100) {
			$('#main-form').removeClass('span9');
			$('#main-form').addClass('span12');
		} else {
			$('#main-form').removeClass('span12');
			$('#main-form').addClass('span9');
		}
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
		$('.carousel-inner').css('overflow', 'visible');
		$('#prev-button').removeClass('disabled');
		$('#add-button').removeClass('disabled');
		
		if ($('.carousel-inner .item:first').hasClass('active')) {
			$('#prev-button').addClass('disabled');
			$('#people-table').datagrid('reload');
			$('#people-div').height($(window).height()*.6);
		} 
		else if ($('.carousel-inner .item:last').hasClass('active')) {
			$('#add-button').addClass('disabled');
		}
	});

	$('#main-container').on('slide', function() {
		$('.carousel-inner').css('overflow', 'hidden');
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