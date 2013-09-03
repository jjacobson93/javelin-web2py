!function($) {
	var jTable = function (element, options) {
		var table = this;

		this.$element = $(element);

		this.isLoading = true;

		if (!this.isInit && options.columns) {
			// Set initial values
			this.options = $.extend(true, {}, $.fn.jTable.defaults, options);
			this.pageIndex = 0;
			this.pages = 0;

			if (!this.$element.hasClass('jtable-table-body'))
				this.$element.addClass('jtable-table-body');

			// Create wrapper
			var wrapper = $('<div class="jtable-wrapper"/>');

			// Create header
			var header = $('<div class="row">'+ 
				'<div class="col-6 col-md-6"><div class="col-12 col-md-12"><h2 class="jtable-title">' +
				this.options.title + '</h2></div></div></div>');
			this.$header = header;

			// Create search control and append to header
			var form = $('<div class="col-6 col-md-6 col-sm-12 form-inline">'+
				'<div class="form-group jtable-search col-6 col-xs-12 col-sm-6">'+
					'<input class="form-control" type="search" placeholder="Search"></div></div></div>');
			this.$form = form.find('.jtable-search');
			header.append(form);

			// Bind keyup event to search control for filtering
			this.$form.find('input[type="search"]').on('keyup', function(e) {
				var val = this.value;
				table.searchFilter(val);
			});

			// Create filter
			if (options.filter) {
				var filter = $('<div class="col-6 col-xs-12 col-sm-6 jtable-filter"><select class="form-control ' + options.filter.class + '"/></div>');
				$.each(options.filter.options, function(i, e) {
					filter.find('select').append('<option value="' + e.value + '">' + e.label + '</option>');
				});
				filter.find('select').on('change', function(e) {
					if (!table.isLoading) {
						var newData = options.filter.fn($(this).val(), table.options.data);
						table.currentData = newData;
						table.render(newData);
					}
				});
				this.$filter = filter;
				header.children('div:last').prepend(filter);
			}

			// Create table div
			var tableRow = this.$element.wrap($('<div class="row jtable-table-body"/>')).parent();

			tableRow.css({
				'max-height': this.options.maxHeight
			});

			// Create pagination
			var pagination = $('<ul class="pagination jtable-pagination pull-right">' +
				'<li class="jtable-prev disabled"><a href="#">&larr; Previous</a></li>' +
				'<li class="jtable-next disabled"><a href="#">Next &rarr;</a></li></ul>');
			this.$pagination = pagination;

			// Create footer
			var showing = $('<span class="jtable-info pull-left">Showing 0 to 0 of 0 entries</span>');
			var sizing = $('<div class="btn-group jtable-sizing" data-toggle="buttons">' +
				'<label class="btn btn-default disabled' + ((this.options.pageSize == 10) ? ' active' : '') + '">' +
					'<input type="radio" name="jtable-pagesize" id="jtable-pagesize-10">10' +
				'</label>' +
				'<label class="btn btn-default disabled' + ((this.options.pageSize == 25) ? ' active' : '') + '">'+
					'<input type="radio" name="jtable-pagesize" id="jtable-pagesize-25">25'+
				'</label>'+
				'<label class="btn btn-default disabled' + ((this.options.pageSize == 50) ? ' active' : '') + '">'+
					'<input type="radio" name="jtable-pagesize" id="jtable-pagesize-50">50'+
				'</label>'+
				'<label class="btn btn-default disabled' + ((this.options.pageSize == 100) ? ' active' : '') + '">'+
					'<input type="radio" name="jtable-pagesize" id="jtable-pagesize-100">100'+
				'</label></div>');
			sizing.find('.btn').each(function(i, e) {
				$(e).on('click', function() {
					if (!$(this).hasClass('disabled')) {
						table.pageIndex = 0;
						table.options.pageSize = parseInt($(this).text());
						table.render(table.currentData);
					}
				});
			});

			this.$sizing = sizing;
			this.$showing = showing;
			var sizeColumn = $('<div class="col-6 col-sm-6"/>').append(showing).append(sizing);
			var footer = $('<div class="row"></div>');
			footer.append(sizeColumn);
			footer.append(pagination.wrap('<div class="col-6 col-sm-6"/>').parent());

			// Add elements to wrapper
			wrapper = tableRow.wrap(wrapper).parent();
			wrapper.prepend(header);
			wrapper.append(footer);

			// Create table header cells
			var thead = $('<thead><tr/></thead>');
			var row = thead.find('tr');
			$.each(this.options.columns, function(i, e) {
				var cell = $('<th class="jtable-sort">' + e.label + '</th>');
				cell.on('click', function(e) {
					table.headerClick(e);
				});
				row.append(cell);
			});

			var cloneThead = thead.clone().addClass("jtable-thead-clone");
			cloneThead.find('th').empty();
			cloneThead.find('th').removeClass('jtable-sort');
			cloneThead.find('th').css({
				'height': 0,
				'margin': 0,
				'padding': 0,
				'border': 'none'
			});

			this.$element.prepend(cloneThead);
			
			var headerTable = thead.wrap('<table></table>').parent();
			var headerTableRow = headerTable.wrap('<div class="row jtable-table-head"/>').parent();
			this.$headerTable = headerTable;
			headerTableRow.insertBefore(tableRow);

			// Add temporary loading row
			this.$tbody = $('<tbody/>');
			this.$tbody.append('<tr class="jtable-loading">' +
				'<td colspan="' + this.options.columns.length +
				'">Loading...</td></tr>');
			this.$element.append(this.$tbody);

			// Load Data
			this.loadData();

			this.isInit = true;
		}
	}

	jTable.prototype = {
		constructor: jTable,
		loadData: _loadData,
		render: _render,
		nextPage: _nextPage,
		prevPage: _prevPage,
		headerClick: _headerClick,
		sortTable: _sortTable,
		searchFilter: _searchFilter,
		reload: _reload,
		seamlessReload: _seamlessReload,
		setTitle: _setTitle
	};

	function _render(data) {
		var table = this;
		var newTbody = $('<tbody/>');
		var pagination = this.$pagination;
		$('li:gt(0)', pagination).filter(':not(:last)').remove();
		$('li', pagination).addClass('disabled');

		if (data.length) {
			var dataLength = data.length;

			this.pages = Math.ceil(data.length / this.options.pageSize);
			var start = (this.pageIndex - 2 >= 0) ? this.pageIndex - 2 : 0;
			var end = (start + 5 <= this.pages) ? start + 5 : this.pages;
			if ((end - start) != 5 && this.pageIndex - 2 >= 0)
				start = end - 5;
			for (var i = start; i < end; i++) {
				$('<li' + ((table.pageIndex == i) ? ' class="active"' : '') + '>' +
					'<a href="#">' + (i+1) + '</a></li>').insertBefore(pagination.find('li:last')[0]);
			}

			var startIndex = this.pageIndex*this.options.pageSize;
			var endIndex = startIndex + this.options.pageSize;

			data = data.slice(startIndex, endIndex);

			$.each(data, function(i, d) {
				var row = $('<tr/>')
				$.each(table.options.columns, function(j, e) {
					row.append('<td>' + ((d[e.key] != undefined) ? d[e.key] : '') + '</td>');
					if (table.options.createdRow)
						row = table.options.createdRow(row, d);
				});
				newTbody.append(row);
			});

			if (this.pageIndex > 0)
				pagination.find('.jtable-prev').removeClass('disabled');
			else
				pagination.find('.jtable-prev').addClass('disabled');

			if (this.pageIndex + 1 == this.pages)
				pagination.find('.jtable-next').addClass('disabled');
			else
				pagination.find('.jtable-next').removeClass('disabled');

			pagination.find('.jtable-prev').off('click');
			pagination.find('.jtable-prev').on('click', function(e) {
				e.preventDefault();
				if (!$(this).hasClass('disabled'))
					table.prevPage();
			});

			pagination.find('.jtable-next').off('click');
			pagination.find('.jtable-next').on('click', function(e) {
				e.preventDefault();
				if (!$(this).hasClass('disabled'))
					table.nextPage();
			});

			$('li:gt(0)', pagination).filter(':not(:last)').each(function() {
				$(this).off('click');
				$(this).on('click', function(e) {
					e.preventDefault();
					if (!$(this).hasClass('active')) {
						table.pageIndex = parseInt($(this).text()) - 1;
						table.render(table.currentData);
					}
				});
			});

			this.$tbody = newTbody;
			this.$element.find('tbody').replaceWith(newTbody);
			var headerCells = this.$headerTable.find('tr').find('th');
			this.originalWidths = [];
			this.$element.find('.jtable-thead-clone').find('th').each(function(i, e) {
				var width = $(e).outerWidth();
				$(headerCells[i]).css('width', width);
			});

			this.$sizing.find('.btn').removeClass("disabled")
			this.$showing.html('Showing ' + (startIndex + 1) + ' to ' + 
				((endIndex > dataLength) ? dataLength : endIndex) +
				' of ' + dataLength + ' entries');
		} else {
			newTbody.append('<tr class="jtable-empty"><td colspan="' + this.options.columns.length + '">No Records</td></tr>');
			this.$tbody = newTbody;
			this.$element.find('tbody').replaceWith(newTbody);
			this.$sizing.find('.btn').addClass("disabled")
			this.$showing.html('Showing 0 to 0 of 0 entries');
		}

		this.isLoading = false;
		this.options.loaded();
		this.$element.trigger('loaded');
	}

	function _nextPage() {
		this.pageIndex++;
		if (this.pageIndex > this.pages)
			this.pageIndex = this.pages;
		this.render(this.currentData);
	}

	function _prevPage() {
		this.pageIndex--;
		if (this.pageIndex < 0)
			this.pageIndex = 0;
		this.render(this.currentData);
	}

	function _loadData() {
		var table = this;
		this.currentData = undefined;
		var data = this.options.ajax.data;
		var source = this.options.ajax.source;
		var error = this.options.ajax.error;
		if (!data)
			data = {};
		$.ajax({
			type: "POST",
			url: source,
			data: data,
			dataType: 'json',
			success: function(data) {
				table.currentData = data;
				table.options.data = data;
				table.render(data);
			},
			error: function(e) {
				error();
				table.currentData = [];
				table.options.data = [];
				table.render(data);
			}
		});
	}

	function _searchFilter(val) {
		if (!this.isLoading) {
			var re = new RegExp(val, "i");
			var data = [];
			$.each(this.currentData, function(i, e) {
				var row = $.map(e, function(val, key) { return val; }).join('');
				if (row.search(re) >= 0)
					data.push(e);
			});

			this.render(data);
		}
	}

	function _sortTable(direction, headerIndex) {
		var sortProperty = this.options.columns[headerIndex].key;
		this.currentData = _.sortBy(this.currentData, sortProperty);
		if (direction == 'desc') this.currentData.reverse();
		this.render(this.currentData);
	}

	function _headerClick(e) {
		if (this.isLoading != undefined && this.isLoading == false) {
			this.pageIndex = 0;
			var sortDirection = 'none';
			if ($(e.target).hasClass("jtable-sort-asc")) {
				sortDirection = 'desc';
			} else {
				sortDirection = 'asc'
			}
			this.$headerTable.find('.jtable-sorted').removeAttr('class').addClass('jtable-sort');

			if (sortDirection == 'desc')
				$(e.target).addClass('jtable-sort-desc jtable-sorted');
			else if (sortDirection == 'asc')
				$(e.target).addClass('jtable-sort-asc jtable-sorted');

			var headerIndex = this.$headerTable.find('th').index(e.target);

			this.sortTable(sortDirection, headerIndex);
		}
	}

	function _reload(ajax) {
		if (ajax != undefined)
			$.extend(true, this.options.ajax, ajax);
		this.$tbody.html('<tr class="jtable-loading"><td colspan="' + this.options.columns.length + '">Loading...</td></tr>');
		this.$sizing.find('.btn').addClass("disabled");
		this.$showing.html('Showing 0 to 0 of 0 entries');
		$('li:gt(0)', this.$pagination).filter(':not(:last)').remove();
		$('li', this.$pagination).addClass('disabled');
		this.loadData();
	}

	function _seamlessReload(ajax) {
		if (ajax != undefined)
			$.extend(true, this.options.ajax, ajax);
		this.loadData();
	}

	function _setTitle(title) {
		this.options.title = title;
		this.$header.find('.jtable-title').html(title);
	}

	$.fn.jTable = function (option, value) {
		return this.each(function () {
			var $this = $(this);
			var data = $this.data('jTable');
			var options = typeof option === 'object' && option;

			if (!data) $this.data('jTable', (data = new jTable($this, options)));
			if (typeof option === 'string') data[option](value);
		});
	};

	$.fn.jTable.defaults = {
		maxHeight: 300,
		pageSize: 10,
		title: '',
		ajax: {
			error: function() {
				console.log("ERROR! There was an error loading the data");
			}
		},
		loaded: function() {}
	};

	$.fn.jTable.Constructor = jTable;

}(window.jQuery);