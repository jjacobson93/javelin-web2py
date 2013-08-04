// SETCOLUMNWIDTHS OVERRIDE
$.fn.datagrid.Constructor.prototype.setColumnWidths = function () {
	if (!this.$sizingHeader) return;
 
	this.$element.prepend(this.$sizingHeader);
 
	var $sizingCells = this.$sizingHeader.find('th');
	var columnCount = $sizingCells.length;
	var tableWidth = $sizingCells.parent().width(); // Used to calculate the width percent
 
	function matchSizingCellWidth(i, el) {
		// if (i === columnCount - 1) return; // Shouldn't every cell change width when resized?
		var width = $sizingCells.eq(i).width();
		$(el).width((width/tableWidth)*100 + "%"); // Using percentage of table width
	}
 
	this.$colheader.find('th').each(matchSizingCellWidth);
 
	// Add the header row to the tbody 
	var headerRow = this.$colheader.clone();
	headerRow.find('i').remove(); //Remove the sort icon
	this.$tbody.prepend(headerRow);
	// Hide the header row
	headerRow.find('th').each(function(i,e) { 
		$(e).css({'height':'0px', 
			'line-height':'0px', 
			'overflow':'hidden', 
			'padding':'0px',
			'border':'none'});
	});
 
	this.$tbody.find('tr:first > td').each(matchSizingCellWidth);
	// Fix border issue
	this.$tbody.find('tr:not(tr:first):first td').each(function(i, el) {
		$(el).css('border-top', 'none');
	});
 
	this.$sizingHeader.detach();
}

$.fn.datagrid.Constructor.prototype.seamlessReload = function () {
	var self = this;

	this.options.dataSource.data(this.options.dataOptions, function (data) {
		var itemdesc = (data.count === 1) ? self.options.itemText : self.options.itemsText;
		var newRow = '';

		self.$footerchildren.css('visibility', function () {
			return (data.count > 0) ? 'visible' : 'hidden';
		});

		self.$pageinput.select2('val', data.page);
		self.$pageslabel.text(data.pages);
		self.$countlabel.text(data.count + ' ' + itemdesc);
		self.$startlabel.text(data.start);
		self.$endlabel.text(data.end);

		self.updatePageDropdown(data);
		self.updatePageButtons(data);

		self.$tbody.find('tr').eq(0).remove();
		var currentData = self.$tbody.find('tr');
		$.each(currentData, function(index, row) {
			if (data.data[index]) {			
				var isSame = true;
				newRow += '<tr' + ((data.data[index]['id']) ? ' id="' + data.data[index]['id'] + '"' : '') + '>';
				$.each(self.columns, function (index2, column) {
					newRow += '<td data-value="' + String(data.data[index][column.property]) + '">' + data.data[index][column.property] + '</td>';
					if ($(row).find('td').eq(index2).attr("data-value") != String(data.data[index][column.property])) {
						if (isSame)
							isSame = false;
					}
				});
				newRow += '</tr>';

				if (!isSame) {
					var id = $(newRow).attr('id');
					$('#' + id).html($(newRow).html());
				}
			}
			newRow = '';
		});

		if (!currentData) {
			rowHTML = self.placeholderRowHTML('0 ' + self.options.itemsText);
			self.$tbody.html(rowHTML);
		}

		self.stretchHeight();

		self.$element.trigger('loaded');
	});
}

$.fn.datagrid.Constructor.prototype.renderData = function () {
	var self = this; //The datagrid

	this.$tbody.html(this.placeholderRowHTML(this.options.loadingHTML));

	this.options.dataSource.data(this.options.dataOptions, function (data) {
		var itemdesc = (data.count === 1) ? self.options.itemText : self.options.itemsText;
		var rowHTML = '';

		self.$footerchildren.css('visibility', function () {
			return (data.count > 0) ? 'visible' : 'hidden';
		});

		self.$pageinput.select2('val', data.page);
		self.$pageslabel.text(data.pages);
		self.$countlabel.text(data.count + ' ' + itemdesc);
		self.$startlabel.text(data.start);
		self.$endlabel.text(data.end);

		self.updatePageDropdown(data);
		self.updatePageButtons(data);

		$.each(data.data, function (index, row) {
			rowHTML += '<tr' + ((row['id']) ? ' id="' + row['id'] + '"' : '') + '>';
			$.each(self.columns, function (index, column) {
				rowHTML += '<td data-value="' + String(row[column.property]) + '">' + row[column.property] + '</td>';
			});
			rowHTML += '</tr>';
		});

		if (!rowHTML) rowHTML = self.placeholderRowHTML('0 ' + self.options.itemsText);

		self.$tbody.html(rowHTML);
		self.stretchHeight();

		self.$element.trigger('loaded');
	});

}