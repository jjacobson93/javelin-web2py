app.directive('ngJtable', ['$interpolate', '$http', '$sce', '$timeout', function($interpolate, $http, $sce, $timeout) {
	var START = $interpolate.startSymbol();
	var END = $interpolate.endSymbol();
	return {
		restrict: 'A',
		scope: {
			'table': '=ngJtable'
		},
		template: 
		// '<div class="row">' +
		// '	<div class="col-sm-8">' +
		// '		<h1>' + START + 'title' + END + '</h1>' +
		// '	</div>' +
		// '	<div class="col-sm-4">' +
		// '		<input class="form-control ng-jtable-search" type="text" placeholder="Search" ng-model="searchValue" ng-change="search()">' +
		// '	</div>' +
		// '</div>' +
		'<div class="ng-jtable-header">\n' +
		'	<table class="' + START + ' classes ' + END + '">\n' +
		'		<thead>\n' +
		'			<tr><th class="ng-jtable-sort" ng-class="{\'ng-jtable-asc\': (sortedColumn == col.key && sortDirection == 1), \'ng-jtable-desc\': (sortedColumn == col.key && sortDirection == 2)}" ng-repeat="col in columns" ng-click="sortColumn(col.key)">' + START + ' col.label ' + END + '</th></tr>\n' +
		'		</thead>\n' +
		'	</table>\n' +
		'</div>\n' +
		'<div class="ng-jtable-body">\n' +
		'	<table class="' + START + ' classes ' + END + '">\n' +
		'		<thead>\n' +
		'			<tr><th ng-repeat="col in columns" style="height:0;margin:0;padding:0;border:none"></th></tr>\n' +
		'		</thead>\n' +
		'		<tbody>\n' +
		'			<tr ng-if="isLoading" style="text-align:center;font-weight:bold;"><td style="border:none" colspan="' + START + 'columns.length' + END + '"><i class="fa fa-circle-o-notch fa-spin"></i> Loading Data</td></tr>\n' +
		'			<tr ng-if="rows.length == 0 && !isLoading" style="text-align:center;font-weight:bold;"><td style="border:none" colspan="' + START + 'columns.length' + END + '">No Results</td></tr>\n' +
		'			<tr ng-repeat-start="row in rows" ng-class="{\'even-row\': ($index%2 == 0), \'odd-row\': ($index%2 == 1)}" ng-click="rowClick(row)">\n' +
		'				<td ng-repeat="col in columns" ng-bind-html="\'<span>\' + (row[col.key] || trustAsHtml(col.template)) + \'</span>\'"></td>\n' +
		'			</tr>\n' +
		'			<tr ng-repeat-end class="expand-row" ng-if="expandedRow.row == row" style="width: 100%">\n' +
		'				<td colspan="' + START + 'columns.length' + END + '">\n' +
		'					<div ng-if="!expandedRow.loaded" style="width:100%;text-align:center;font-weight:bold;"><i class="fa fa-circle-o-notch fa-spin"></i> Loading Data</div>\n' +
		'					<div ng-if="expandedRow.loaded" style="width:100%">\n' +
		'						<div ng-if="expandedRow.type == \'form\'">\n' +
		'							<h3>' + START + 'expandedRow.title' + END + '</h3>\n'+
		'							' + START + 'expandedRow.data' + END + '\n' +
		'						</div>\n' +
		'						<div ng-if="expandedRow.type == \'readable\'">\n' +
		'						</div>\n' +
		'					</div>\n' +
		'				</td>\n' +
		'			</tr>\n' +
		'		</tbody>\n' +
		'	</table>\n' +
		'</div>\n' +
		'<div class="row">\n' +
		'	<div class="col-sm-6">\n' +
		'		<span>Showing ' + START + '(numberOfEntries > 0) ? startIndex + 1 : 0' + END +' to ' + START + ' endIndex ' + END + ' of ' + START + ' numberOfEntries ' + END + ' entries &nbsp;&nbsp;&nbsp;</span>\n' +
		'		<select ui-select2="{minimumResultsForSearch: -1}" ng-model="pageSizeSelect.selected" ng-change="pageSizeSelect.change()">\n' +
		'			<option ng-repeat="opt in pageSizeSelect.options">' + START + ' opt ' + END + '</option>\n' +
		'		</select>\n' +
		'		<span>per page</span>\n' +
		'	</div>\n' +
		'	<div class="col-sm-6">\n' +
		'		<ul class="pagination pull-right">\n' +
		'			<li ng-class="{disabled: pageIndex == 0}"><a ng-click="prevPage()">&lsaquo; Previous</a></li>\n' +
		'			<li ng-repeat="i in pageNumbers" ng-class="{active: pageIndex == i}"><a ng-click="setPage(i)">' + START + 'i + 1' + END +'</a></li>\n' +
		'			<li ng-class="{disabled: !(pageIndex < numberOfPages - 1)}"><a ng-click="nextPage()">Next &rsaquo;</a></li>\n' +
		'		</ul>\n' +
		'	</div>\n' +
		'</div>',
		link: function($scope, $elem, attrs) {
			var table = $scope.table;

			$scope.classes = table.classes;
			$scope.columns = table.columns;
			$scope.title = table.title;
			$scope.filteredData = [];
			$scope.rows = [];
			$scope.isLoading = false;
			$scope.expandedRow = {
				row: undefined,
				data: undefined,
				type: undefined,
				title: undefined,
				loaded: false
			};
			$scope.trustAsHtml = $sce.trustAsHtml;

			// Set up row clicking
			$scope.rowClick = function(row) {
				$scope.expandedRow.data = undefined;
				$scope.expandedRow.type = undefined;
				$scope.expandedRow.title = undefined;
				$scope.expandedRow.loaded = false;
			
				if ($scope.expandedRow.row == row) {
					$scope.expandedRow.row = undefined;
				} else {
					if (table.rowClick != undefined) {

						if (table.rowClick.data != undefined) {
							table.rowClick.data(row, function(data) {
								$scope.expandedRow.row = row;
								$timeout(function() {
									$scope.expandedRow.data = data.results;
									$scope.expandedRow.type = data.type;
									$scope.expandedRow.title = data.title;
									$scope.expandedRow.loaded = true;
								}, 2000);
							});
						}

						// if (table.rowClick.action != undefined) {
						// 	table.rowClick.action(row, function(result){

						// 	});
						// }
					}
				}
			};

			// Get data
			$scope.data = undefined;
			if (table.data) {
				$scope.data = table.data;
			} else if (table.getData) {
				$scope.isLoading = true;
				$http.get(table.getData.url).success(function(data) {
					var prop = table.getData.property;
					$scope.data = $scope.table.data = (prop) ? data[prop] : data;
					$scope.isLoading = false;
				});
			}
		
			// Show entries select
			$scope.pageSizeSelect = {};
			$scope.pageSizeSelect.options = [10,25,50,100,1000];
			$scope.pageSizeSelect.selected = 10;
			$scope.pageSizeSelect.change = function() {
				pageEntries();
			};

			// Pagination
			$scope.pageIndex = 0;
			$scope.numberOfPages = 1;
			$scope.startIndex = 0;
			$scope.endIndex = 0;

			$scope.prevPage = function() {
				if ($scope.pageIndex > 0) {
					$scope.pageIndex -= 1;
					pageEntries();
				}
			};

			$scope.setPage = function(n) {
				if (n >= 0 && n < $scope.numberOfPages) {
					$scope.pageIndex = n;
					pageEntries();
				}
			};

			$scope.nextPage = function() {
				if ($scope.pageIndex < $scope.numberOfPages - 1) {
					$scope.pageIndex += 1;
					pageEntries();
				}
			};

			// Sorting 
			$scope.sortedColumn = undefined;
			$scope.sortDirection = 0;
			$scope.sortColumn = function(colKey) {
				if ($scope.sortedColumn == colKey) {
					$scope.sortDirection = ($scope.sortDirection%2) + 1;
				} else {
					$scope.sortedColumn = colKey;
					$scope.sortDirection = 1;
				}

				if ($scope.sortDirection == 0) {
					$scope.sortedColumn = undefined;
				} else {
					$scope.data = _.sortBy($scope.data, colKey);
					if ($scope.sortDirection == 2) $scope.data.reverse();
					filterDataAndPageEntries();
				}
			}


			// Searching
			$scope.searchValue = '';
			var filterDataAndPageEntries = function() {
				if ($scope.searchValue !== undefined) { 
					var lowerValues = $scope.searchValue.toLowerCase().split(' ');
					$scope.filteredData = [];

					for (var i = 0; i < $scope.data.length; i++) {
						var obj = $scope.data[i];
						var row = Object.keys(obj).map(function(k){return obj[k]}).join(' ');
						var isAMatch = true;
						for (j in lowerValues) {
							var lower = lowerValues[j].toLowerCase();
							if (row.toLowerCase().indexOf(lower) == -1) {
								isAMatch = false;
								break;
							}
						}

						if (isAMatch) $scope.filteredData.push($scope.data[i]);
					};

					$scope.pageIndex = 0;
					pageEntries();
				}
			};

			var columnWidths = function() {
				var headerCells = $elem.find('.ng-jtable-body').find('tr').find('th');
				$elem.find('.ng-jtable-header').find('thead').find('th').each(function(i, e) {
					var width = $(e).outerWidth();
					$(headerCells[i]).css('width', width);
				});
			};

			var range = function(a, b) {
				if (b == undefined) {
					return Array.apply(null, new Array(a)).map(function(e, i){return i});
				} else {
					return Array.apply(null, new Array(b - a)).map(function(e, i) {return i + a});
				}
			};

			var pageEntries = function() {
				$scope.numberOfEntries = $scope.filteredData.length;

				var pageSize = parseInt($scope.pageSizeSelect.selected);
				var pageIndex = $scope.pageIndex;

				$scope.numberOfPages = Math.ceil($scope.numberOfEntries/pageSize);

				$scope.startIndex = pageIndex*pageSize;
				$scope.endIndex = Math.min($scope.startIndex + pageSize, $scope.numberOfEntries);

				var start = (pageIndex - 2 >= 0) ? pageIndex - 2 : 0;
				var end = (start + 5 <= $scope.numberOfPages) ? start + 5 : $scope.numberOfPages;
				if ((end - start) != 5 && pageIndex - 2 >= 0)
					start = end - 5;

				$scope.pageNumbers = range(start, end);

				$scope.rows = $scope.filteredData.slice($scope.startIndex, $scope.endIndex);
			};
			
			$scope.$watch('table.data', function(data) {
				$scope.data = (data) ? data : [];
				filterDataAndPageEntries();
				columnWidths();
			});

			$scope.$watch('table.search.value', function(val) {
				$scope.searchValue = val;
				filterDataAndPageEntries();
			});
		}
	};
}]);