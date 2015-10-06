app.factory('PeopleFactory', ['$http', function($http) {
	return {
		get: function(params) {
			return $http.get('/api/people.json', {params: params});
		},
		filter: function(criteria) {
			return $http.get('/api/people/filter')
		}
	}
}]);