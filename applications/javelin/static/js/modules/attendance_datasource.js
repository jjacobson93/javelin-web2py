var AttendanceDataSource = function(options) {
	this._formatter = options.formatter;
	this._columns = options.columns;
	this._delay = options.delay || 0;
	this._event_id = options.event_id;
	// this._data = options.data;
};

AttendanceDataSource.prototype = {
	columns: function() {
		return this._columns;
	},

	data: function(options, callback) {
		var event_id = this._event_id;
		$.ajax({
			type: "POST",
			url: "/orientation/call/json/attendance_data",
			data: {
				'event_id' : event_id
			},
			dataType: "json",
			success: function(data) {
				var self = this;
				setTimeout(function () {
					// SEARCHING
					if (options.search) {
						data = _.filter(data, function (item) {
							for (var prop in item) {

								if (!item.hasOwnProperty(prop)) continue;
								if (item[prop] != null && ~item[prop].toString().toLowerCase().indexOf(options.search.toLowerCase())) return true;
							}
							return false;
						});
					}

					// FILTERING
					if (options.filter) {
						data = _.filter(data, function (item) {
							switch(options.filter.value) {
								case 'leaders':
									if(item.person_grade != 9 && item.person_leader) return true;
									break;
								case 'freshmen':
									if(item.person_grade == 9) return true;
									break;
								default:
									return true;
									break;
							}
						});
					}

					var count = data.length;

					// SORTING
					if (options.sortProperty) {
						data = _.sortBy(data, options.sortProperty);
						if (options.sortDirection === 'desc') data.reverse();
					}

					// PAGING
					var startIndex = options.pageIndex * options.pageSize;
					var endIndex = startIndex + options.pageSize;
					var end = (endIndex > count) ? count : endIndex;
					var pages = Math.ceil(count / options.pageSize);
					var page = options.pageIndex + 1;
					var start = startIndex + 1;

					data = data.slice(startIndex, endIndex);

					if (self._formatter) self._formatter(data);

					$(data).each(function(index) {
						data[index]['attendance_present'] = (data[index]['attendance_present']) ? true : false;
					});

					callback({ data: data, start: start, end: end, count: count, pages: pages, page: page });

				}, this._delay);
			},
			error: function() {
				displayError("Could not retrieve records.");
				callback({ data: [], start: 0, end: 0, count: 0, pages: 0, page: 0 });
			}
		});
	}
};