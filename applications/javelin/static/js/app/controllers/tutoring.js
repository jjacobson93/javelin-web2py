app.controller('TutoringController', ['$scope', '$http', function($scope, $http) {

	$scope.subjects = [];

	$http.get('/api/tutoring/subjects').success(function(data) {
		$scope.subjects = data.data;
	}).error(function(data) {
		console.log("ERROR:", data);
	});

}]);