var app = angular.module('JavelinApp',
	['ngRoute', 'ngResource', 'ngSanitize', 'ngAnimate', 
	 'ui.bootstrap', 'ui.calendar', 'ui.router', 'ui.select2', 
	 'toggle-switch'], 
	['$interpolateProvider', function($interpolateProvider) {
		$interpolateProvider.startSymbol('{[');
		$interpolateProvider.endSymbol(']}');
	}]
);

app.config(['$stateProvider', '$urlRouterProvider', 
	function($stateProvider, $urlRouterProvider) {
		$urlRouterProvider.otherwise(function($injector, $location) {
			$injector.invoke(['AuthService', function(AuthService) {
				var isAuthenticated = AuthService.isAuthenticated();
				$location.path((isAuthenticated) ? '/' : '/login');
			}]);
		});

		$stateProvider	
			.state('login', {
				url: '/login',
				templateUrl: '/user/login'
			})

			.state('dashboard', {
				url: '/',
				templateUrl:'/dashboard',
				controller: 'DashboardController'
			})

			.state('people', {
				url: '/people',
				templateUrl: '/people',
				controller: 'PeopleController'
			})
				.state('people.detail', {
					url: '/:id'
				})

			.state('groups', {
				url: '/groups',
				templateUrl: '/groups',
				controller: 'GroupsController'
			})

			.state('events', {
				url: '/events',
				templateUrl: '/events',
				controller: 'EventsController'
			})

			.state('tutoring', {
				url: '/tutoring',
				templateUrl: '/tutoring',
				controller: 'TutoringController'
			})

			.state('admin', {
				url: '/admin',
				templateUrl: '/jadmin',
				controller: 'AdminController'
			});
	}
]);

app.run(['$rootScope', '$state', '$window', 'AuthService', function($rootScope, $state, $window, AuthService) {
	$rootScope.$on('$stateChangeStart', function(event, toState, toParams, fromState, fromParams) {
		var isAuthenticated = AuthService.isAuthenticated();

		if ((toState.name != 'login' && !isAuthenticated) || (toState.name == 'login' && isAuthenticated)) {
			// $state.transitionTo('login')
			$window.location = '/'
			event.preventDefault();
		}
	})
}]);