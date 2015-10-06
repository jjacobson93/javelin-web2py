app.controller('MainController', ['$scope', '$location', '$state', function($scope, $location, $state) {
	$scope.$location = $location;
	$scope.$state = $state;
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