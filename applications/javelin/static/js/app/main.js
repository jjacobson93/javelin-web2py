var app = angular.module('JavelinApp',
	['ngRoute', 'ngResource', 'ngSanitize', 'ui.calendar'], 
	['$interpolateProvider', function($interpolateProvider) {
		$interpolateProvider.startSymbol('{[');
		$interpolateProvider.endSymbol(']}');
	}]
);

app.config(['$routeProvider', '$locationProvider', 
	function($routeProvider, $locationProvider) {
		$routeProvider

		.when('/', {
			templateUrl:'/dashboard',
			controller: 'DashboardController'
		})

		// .when('/login', {
		// 	templateUrl: '/user/login'
		// })

		// .when('/search', {
		// 	templateUrl:'/search',
		// 	controller: 'SearchController'
		// })

		.when('/people', {
			templateUrl: '/people',
			controller: 'PeopleController'
		})

		.when('/groups', {
			templateUrl: '/groups',
			controller: 'GroupsController'
		})

		.when('/events', {
			templateUrl: '/events',
			controller: 'EventsController'
		})

		.when('/messages', {
			templateUrl: '/messages',
			controller: 'MessagesController'
		})

		.otherwise({
			redirectTo: '/'
		});
	}
]);