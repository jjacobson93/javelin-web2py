app.controller('AdminController', ['$scope', function($scope) {
	// $scope.$parent.cancelSearch();
	$scope.controllerName = "Admin";
	$scope.isLoaded = false;

	$scope.load = function() {
		$scope.isLoaded = true;
	};

}]);