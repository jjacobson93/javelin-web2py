app.controller('EventsController', ['$scope', '$http', function($scope, $http) {
	// $scope.$parent.cancelSearch();
	$scope.controllerName = "Events";

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