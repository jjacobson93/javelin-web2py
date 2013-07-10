$(document).ready(function() {
	$('#people-table').datagrid({
		dataSource: new PeopleDataSource({
			columns: [
				{
					property: 'id',
					label: 'ID',
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
					property: 'phone',
					label: 'Phone',
					sortable: true
				}
			]
		}),
		stretchHeight: true
	});

	$('#people-table').on('loaded', function() {
		$('.grid-pagesize').select2();
		$('.grid-pager select').select2({ placeholder: "1" });
	});
	// $('.grid-pager select').select2('val', $('#people-table').datagrid('pageNum'));


	$('#people-div').height($(window).height()*.7);

	$('#person-pane').on('keyup', 'input,textarea', function() {
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
		var td = $(this).find("td");
		var p_id = td.eq(0).html();
		
		loadRecord(p_id);
		
		$('#main-container').carousel('next');
		$('#main-container').carousel('pause');
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
		// $('#save-button').removeClass('disabled');
		$('#add-button').removeClass('disabled');
		// $('#next-button').removeClass('disabled');
		
		if ($('.carousel-inner .item:first').hasClass('active')) {
			$('#prev-button').addClass('disabled');
			// $('#save-button').addClass('disabled');
		} 
		else if ($('.carousel-inner .item:last').hasClass('active')) {
			$('#next-button').addClass('disabled');
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
			saveChanges();
			btn.button('reset');
		}
	});

	$('#prev-button').on('click', function(e) {
		e.preventDefault();
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
		var saved = saveChanges();
		if (saved) {
			$('#main-container').carousel('prev');
			$('#save-approve-modal').modal('hide');
		}
	});

	$('#person-pic').on('click', function() {
		$('#current-pic').empty();
		$('#current-pic').append($('#person-pic').html());
		$('#current-pic').css("padding", 0);

		$('#upload-pic-modal').modal('show');
	});

	$('#upload-pic-btn').on('click', function() {
		var id = $('#inputID').val();
		var pic = $('#current-pic').find("img").attr("src");
		pic = pic.substr(pic.indexOf(",") + 1);

		$('#upload-pic-modal').modal('hide');

		$.ajax({
			type: "POST",
			url: "/people/update_pic",
			data: {
				"id" : id,
				"pic" : pic
			},
			success: function() {
				loadRecord(id);
				displaySuccess("The picture has been uploaded.")
			},
			error: function() {
				displayError("The picture could not be uploaded.")
			}
		});
	})

	$('#upload-btn').on('click', function(e) {
		e.preventDefault();
		$('#upload-doc-modal').modal({
			show: true,
			keyboard: true
		});
	});

	$('#remove-btn').on('click', function() {
		$('#current-pic').empty();
		$('#current-pic').append($('#person-pic').html());
	});
});

function loadRecord(id) {
	$.ajax({
		type: "POST",
		url: "/people/call/json/record",
		data: {
			"id" : id
		},
		dataType: "json",
		success: function(data) {
			$.each(data, function(k, v) {
				if (k != 'pic')
					$('#' + k).val(v);
			});

			var pic = data['pic']
			$('#person-pic').empty();
			if (pic != null) {
				$('#person-pic').css("padding", 0);
				$('#person-pic').append("<img src='data:image/jpeg;base64," + pic + "' style='height: 172px; width: 180px'>");
			} else {
				$('#person-pic').css("padding", "75px 0"); 
				$('#person-pic').text("No picture");
			}
		},
		error: function() {
			displayError("The record could not be loaded")
			$('#person-pic').empty();
			$('#person-pic').css("padding", "75px 0"); 
			$('#person-pic').text("No picture");
		}
	});
}

function saveChanges() {
	var data = {}
	var saved = false;
	$('#main-form input, #main-form select').each(function(i, e) {
		var id = $(e).attr('id');
		data[id] = $(e).val();
	});
	
	$.ajax({
		type: "POST",
		url: "/people/update_record",
		data: data,
		success: function() {
			saveComplete();
			displaySuccess("The record has been saved.")
		},
		error: function() {
			displayError("The record could not be saved.")
		}
	});

}

function saveComplete() {
	$('#save-button').addClass('disabled');
}