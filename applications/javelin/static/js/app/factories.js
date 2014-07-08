app.factory('PeopleFactory', ['$resource', function($resource) {
	return {
		getPeople: function() {
			return $resource('/api/people.json').query().$promise;
		} 
	}
}]);