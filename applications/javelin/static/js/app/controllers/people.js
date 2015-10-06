app.controller('PeopleController', ['$scope', '$http', '$location', '$state', '$timeout', function($scope, $http, $location, $state, $timeout) {
	// $scope.people = [];
	// $scope.$parent.cancelSearch();
	$scope.controllerName = "People";
	$scope.state = $state;

	$scope.currentPerson = undefined;

	var getPerson = function(id) {
		$http.get('/api/people/' + id).success(function(data) {
			$scope.currentPerson = data.data;
			$location.path('/people/' + $scope.currentPerson.id);
		}).error(function(data) {
			notify("error", "Could not get data");
		});
	}

	if ($state.current.name == 'people.detail') {
		getPerson($state.params.id);
	}

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
		rowClick: function(row, cb) {
			getPerson(row.id);
		},
		resetWidths: false
	};

	$scope.$watch('state.current.name', function(name) {
		if (name == 'people') {
			$timeout(function() {
				$scope.personTable.resetWidths = true;
			}, 1000);
		}
	});

	// $scope.loadData = function() {
	// 	$http.get('/api/people.json').success(function(people) {
	// 		$scope.people = $scope.personTable.data = people['data'];
	// 	});
	// };

	// $scope.loadData();

	
}]);