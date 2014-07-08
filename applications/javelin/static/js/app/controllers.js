app.controller('MainController', ['$scope', '$location', function($scope, $location) {
	$scope.$location = $location;
	$scope.previousLocation = {};
	$scope.isSearching = false;
	// $scope.controllerName = "Dashboard";

	// $scope.searchInput = document.getElementById("#search-input");
	$scope.search = {};
	$scope.search.value = "";
	$scope.search.change = function() {
		$scope.isSearching = true;
		// if (!$scope.isSearching) {
		// 	$scope.isSearching = true;
		// 	if ($scope.previousLocation.path === undefined) {
		// 		$scope.previousLocation.controller = $scope.controllerName;
		// 		$scope.previousLocation.path = $location.path();
		// 		$location.path('/search');
		// 	}
		// }
	};

	$scope.cancelSearch = function() {
		// if ($scope.previousLocation.path === undefined && $location.path() == '/search')
		// 	$scope.previousLocation.path = '/';
		// $location.path($scope.previousLocation.path);
		// $scope.previousLocation.path = undefined;
		// $scope.previousLocation.controller = undefined;
		$scope.isSearching = false;
		$scope.search.value = "";
	};
}]);

app.controller('DashboardController', ['$scope', function($scope) {
	$scope.$parent.controllerName = "Dashboard";
}]);

// app.controller('SearchController', ['$scope', '$http', '$timeout', function($scope, $http, $timeout) {
// 	$scope.$parent.controllerName = "Search";
// 	$scope.$parent.isSearching = true;

// 	$scope.people = [];
// 	$scope.groups = [];
// 	$scope.events = [];

// 	$scope.isLoading = false;
	
// 	var searchTimeout = undefined;
// 	$scope.$watch('$parent.search.value', function(val) {
// 		if (val !== '') {
// 			$scope.isLoading = true;
// 			$timeout.cancel(searchTimeout);
// 			searchTimeout = $timeout(function() {
// 				$http.get('/api/search', {params: {query: val}}).success(function(data) {
// 					var data = data.data;
// 					$scope.people = data.people;
// 					$scope.groups = data.groups;
// 					$scope.events = data.events;
// 					$scope.isLoading = false;
// 				});
// 			}, 700);
// 		}
// 	});

// 	// $scope.$parent.search.value = "";
// 	// if (!$scope.$parent.isSearching) {
// 	// 	$location.path('/');
// 	// }
// }]);

app.controller('PeopleController', ['$scope', '$http', function($scope, $http) {
	// $scope.people = [];
	// $scope.$parent.cancelSearch();
	$scope.$parent.controllerName = "People";

	$scope.personTable = {
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
		title: 'People',
		getData: {
			url: '/api/people',
			property: 'data'
		},
		search: $scope.$parent.search,
		classes: 'table table-striped table-hover',
		rowClick: function(row) {
			
		}
	};

	// $scope.loadData = function() {
	// 	$http.get('/api/people.json').success(function(people) {
	// 		$scope.people = $scope.personTable.data = people['data'];
	// 	});
	// };

	// $scope.loadData();

	
}]);

app.controller('GroupsController', ['$scope', function($scope) {
	// $scope.$parent.cancelSearch();
	$scope.$parent.controllerName = "Groups";

	$scope.$parent.controllerAction = {};
	$scope.$parent.controllerAction.name = "Add Group";
	$scope.$parent.controllerAction.iconClass = "pe-7s-plus pe-lg";
	$scope.$parent.controllerAction.click = function() {
		console.log("Adding new Group");
	};

	$scope.groupsTable = {
		columns: [
			{ 
				'key': 'name',
				'label': 'Name',
			},
			{ 
				'key': 'description',
				'label': 'Description',
			},
			{
				'label': 'Actions',
				'template': '<a class="btn btn-sm red">Delete</a>',
				'ng-click': 'deleteRecord(row)'
			}
		],
		title: 'Groups',
		getData: {
			url: '/api/groups',
			property: 'data'
		},
		classes: 'table table-hover',
		scope: {
			deleteRecord: function(row)	{
				console.log("DELETE ROW: ", JSON.stringify(row));
			}
		},
		searchInput: $scope.$parent.searchInput,
		rowClick: function(row) {
			
		}
	};
}]);

app.controller('EventsController', ['$scope', '$http', function($scope, $http) {
	// $scope.$parent.cancelSearch();
	$scope.$parent.controllerName = "Events";

	$scope.events = [];
	var mainSource = function(start, end, callback) {
        $http.get('/api/events', {
            params: {
                // our hypothetical feed requires UNIX timestamps
                start: Math.round(start.getTime() / 1000),
                end: Math.round(end.getTime() / 1000),
                _: Math.round(new Date().getTime() / 1000)
            }
        }).success(function(data) {
        	$scope.events = data['data'];
            callback(data['data']);
        });
    };

    var filteredSource = [];

    $scope.eventSources = [mainSource];

    $scope.$watch('$parent.search.value', function(val) {
    	if ($scope.uiCalendar) {
    		var lower = val.toLowerCase();
    		var events = $scope.events.filter(function(event) {
    			return ((event.title !== null && event.title.toLowerCase().indexOf(lower) != -1) || 
    				(event.notes !== null && event.notes.toLowerCase().indexOf(lower) != -1));
    		});

			$scope.eventSources[0] = events;
    	}
    });

	$scope.uiConfig = {
		calendar: {
			editable: true,
			aspectRatio: 1.5,
			header: {
				left: 'title',
			},
			buttonText: {
				prev: '<span class="pe-7s-angle-left pe-2x"></span>',
				next: '<span class="pe-7s-angle-right pe-2x"></span>',
				today: 'Today',
				month: 'Month',
				week: 'Week',
				day: 'Day'
			},
			eventClick: function(event, allDay, jsEvent, view) {

			},
			eventDrop: function(event, dayDelta, minuteDelta, allDay, revertFunc, jsEvent, ui, view) {	
				if (event.id) {
					$http
						.put('/api/events/' + event.id, { 
							start_time: event.start.toISOString().replace('T', ' ').replace('Z', '').slice(0, -4),
							end_time: event.end.toISOString().replace('T', ' ').replace('Z', '').slice(0, -4)
						})
						.success(function(data) {
							if (data.error !== undefined) {
								revertFunc();
								notify("error", "Error changing date. Refresh the page and try again.");
							}
							console.log(data);
						})
						.error(function(err) {
							revertFunc();
							notify("error", "Error changing date. Refresh the page and try again.");
							console.log("Error: %s", err);
						});

					// event.start.toISOString()
				} else {
					revertFunc();
				}
			}
		}
	};
}]);

app.controller('MessagesController', ['$scope', function($scope) {
	// $scope.$parent.cancelSearch();
	$scope.$parent.controllerName = "Messages";
}]);