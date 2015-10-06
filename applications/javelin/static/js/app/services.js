app.service('AuthService', [function() {
	this.isAuthenticated  = function() {
		var result = false;

		$.ajax({
			type: 'GET',
			url: '/user/is_authenticated',
			async: false,
			dataType: 'json',
			success: function(data) {
				result = data;
			},
			error: function(data) {
				result = false;
			}
		});

		return result;
	};
}]);

app.service('GroupService', ['$http', function($http) {
	this.addGroup = function(data) {
		return $http.post('/api/groups', data);
	};

	this.deleteGroup = function(id) {
		return $http.delete('/api/groups/' + id);
	};
}]);