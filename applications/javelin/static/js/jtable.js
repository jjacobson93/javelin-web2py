!function($) {
	var jTable = function(options, element) {
		return _initTable(options, element);
	};

	jTable.prototype = {
		constructor: jTable
	};

	$.fn.jTable = function(options) {
		return new jTable(options, this)
	};

	$.fn.jTable.Constructor = jTable;

	function _initTable(options, table) {
		table.isLoading = true;

		if (!table.isInit) {
			// Set initial values
			table.options = options;
			table.pageIndex = 0;
			table.pages = 0;
			table.pageSize = 10;

			if (!table.hasClass('jtable'))
				table.addClass('jtable');

			// Create wrapper
			var wrapper = $('<div class="jtable-wrapper"/>');

			// Create header
			var header = $('<div class="row"><h2 class="jtable-header">' + ((options.title) ? options.title : '') + '</h2></div>');

			// Create search control and append to header
			var search = $('<div class="form-inline pull-right"><div class="form-group"><input class="form-control jtable-search" type="search" placeholder="Search"></div></div>');
			table.search = search.find('.jtable-search');
			header.append(search);

			// Bind keyup event to search control for filtering
			table.search.on('keyup', function(e) {
				var val = this.value;
				_searchFilter(val, table);
			});

			// Create table div
			var tableRow = table.wrap($('<div class="row"/>')).parent();

			// Create footer
			var pagination = $('<ul class="pagination jtable-pagination pull-right">' +
				'<li class="jtable-prev disabled"><a href="#">← Previous</a></li>' +
				'<li class="jtable-next disabled"><a href="#">Next →</a></li></ul>');
			var footer = $('<div class="row"></div>');
			footer.append(pagination);
			table.pagination = pagination;

			// Add elements to wrapper
			wrapper = tableRow.wrap(wrapper).parent();
			wrapper.prepend(header);
			wrapper.append(footer);

			// Create table header cells
			var thead = $('<thead><tr/></thead>');
			var row = thead.find('tr');
			$.each(options.columns, function(i, e) {
				row.append('<th class="jtable-sort">' + e.label + '</th>');
			});
			table.append(thead);

			// Add temporary loading row
			table.tbody = $('<tbody/>');
			table.tbody.append('<tr class="jtable-loading"><td colspan="' + options.columns.length + '">Loading...</td></tr>');
			table.append(table.tbody);

			// Load Data
			_loadData(options.source, options.vars, table);

			table.isInit = true;
		}

		return table;
	}

	// var startIndex = options.pageIndex * options.pageSize;
	// var endIndex = startIndex + options.pageSize;
	// var end = (endIndex > count) ? count : endIndex;
	// var pages = Math.ceil(count / options.pageSize);
	// var page = options.pageIndex + 1;
	// var start = startIndex + 1;

	// data = data.slice(startIndex, endIndex);

	function _draw(table, data) {
		var newTbody = $('<tbody/>');
		if (data.length) {
			table.pages = Math.ceil(data.length / table.pageSize);
			var pages = '';
			var start = (table.pageIndex - 2 >= 0) ? table.pageIndex - 2 : 0;
			var end = (start + 5 <= table.pages) ? start + 5 : table.pages;
			for (var i = start; i < end; i++) {
				pages += '<li' + ((table.pageIndex == i) ? ' class="active"' : '') + '>' +
					'<a href="#">' + (i+1) + '</a></li>';
			}

			var startIndex = table.pageIndex*table.pageSize;
			var endIndex = startIndex + table.pageSize;

			data = data.slice(startIndex, endIndex);

			$.each(data, function(i, d) {
				var row = $('<tr/>')
				$.each(table.options.columns, function(j, e) {
					row.append('<td>' + d[e.key] + '</td>');
				});
				newTbody.append(row);
			});

			var pagination = $('<ul class="pagination jtable-pagination pull-right">' +
				'<li class="jtable-prev disabled"><a href="#">← Previous</a></li>' +
				'<li class="jtable-tmp-pages"></li>' +
				'<li class="jtable-next disabled"><a href="#">Next →</a></li></ul>');

			if (table.pageIndex > 0)
				pagination.find('.jtable-prev').removeClass('disabled');
			else
				pagination.find('.jtable-prev').addClass('disabled');

			if (table.pageIndex == table.pages)
				pagination.find('.jtable-next').addClass('disabled');
			else
				pagination.find('.jtable-next').removeClass('disabled');

			pagination.find('.jtable-prev').off('click');
			pagination.find('.jtable-prev').on('click', function() {
				if (!$(this).hasClass('disabled'))
					_prevPage(table);
			});

			pagination.find('.jtable-next').off('click');
			pagination.find('.jtable-next').on('click', function() {
				if (!$(this).hasClass('disabled'))
					_nextPage(table);
			});

			pagination.find('.jtable-tmp-pages').replaceWith(pages);

			table.pagination.replaceWith(pagination);
			console.log(table.pagination);
		} else {
			newTbody.append('<tr class="jtable-empty"><td colspan="' + table.options.columns.length + '">No Records</td></tr>');
		}

		table.tbody = newTbody;
		table.find('tbody').replaceWith(newTbody);

		table.isLoading = false;
	}

	function _nextPage(table) {
		table.pageIndex++;
		if (table.pageIndex > table.pages)
			table.pageIndex = table.pages;
		_draw(table, table.options.data);
	}

	function _prevPage(table) {
		table.pageIndex--;
		if (table.pageIndex < 0)
			table.pageIndex = 0;
		_draw(table, table.options.data);
	}

	function _loadData(source, data, table) {
		table.data = undefined;
		if (!data)
			data = {};
		$.getJSON(source, data).done(function(data) {
			table.data = data;
			table.options.data = data;
			_draw(table, data);
		});
	}

	function _searchFilter(val, table) {
		if (!table.isLoading) {
			var re = new RegExp(val, "i");
			var data = [];
			$.each(table.data, function(i, e) {
				var row = $.map(e, function(val, key) { return val; }).join('');
				if (row.search(re) >= 0)
					data.push(e);
			});

			_draw(table, data);
		}
	}

}(window.jQuery);