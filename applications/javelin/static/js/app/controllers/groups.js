app.controller('GroupsController', ['$scope', '$modal', '$q', '$http', 'GroupService', function($scope, $modal, $q, $http, GroupService) {
	// $scope.groupsTable = {
	// 	columns: [
	// 		{ 
	// 			'key': 'name',
	// 			'label': 'Name',
	// 		},
	// 		{ 
	// 			'key': 'description',
	// 			'label': 'Description',
	// 		},
	// 		{
	// 			'label': 'Actions',
	// 			'template': '<a class="btn btn-sm red">Delete</a>',
	// 			'ng-click': 'deleteRecord(row)'
	// 		}
	// 	],
	// 	title: 'Groups',
	// 	getData: {
	// 		url: '/api/groups',
	// 		property: 'data'
	// 	},
	// 	classes: 'table table-hover',
	// 	scope: {
	// 		deleteRecord: function(row)	{
	// 			console.log("DELETE ROW: ", JSON.stringify(row));
	// 		}
	// 	},
	// 	searchInput: $scope.$parent.searchInput,
	// 	rowClick: function(row) {
			
	// 	}
	// };

	$scope.groups = [];
	$scope.isLoading = true;

	$http.get('/api/groups', { params: { 'members': true } }).success(function(data) {
		$scope.groups = data.data;
		$scope.isLoading = false;
	});

	$scope.openCreateGroupModal = function() {
		var modalInstance = $modal.open({
			templateUrl: '/groups/create_group',
			controller: 'GroupCreateController',
			size: 'lg',
			resolve: {}
		})

		modalInstance.result.then(function(newGroup) {
			$scope.groups.push(newGroup.data);
		});
	};

	$scope.openDeleteGroupModal = function(group, idx) {
		var modalInstance = $modal.open({
			templateUrl: '/groups/delete_group',
			controller: ['$scope', '$modalInstance', 'GroupService', function($scope, $modalInstance, GroupService) {
				$scope.group = group;

				$scope.deleteGroup = function() {
					GroupService.deleteGroup(group.id).success(function(data) {
						notify('success', "'" + group.name + "' has been deleted.");

						$modalInstance.close(data);
					}).error(function(err) {
						notify('error', "There was an error deleting '" + group.name + "'. Please try again.");
						$modalInstance.dismiss(err);
					});
				};

				$scope.cancel = function() {
					$modalInstance.dismiss('cancel');
				};
			}],
			size: 'sm'
		});

		modalInstance.result.then(function() {
			$scope.groups.splice(idx, 1);
		});
	};

}]);

app.controller('GroupCreateController', [
	'$scope', '$http', '$modalInstance', 'GroupService', 
	function($scope, $http, $modalInstance, GroupService) {
		$scope.group = {};
		$scope.group.is_smart = true;
		$scope.group.permission = "user";

		var year = new Date().getFullYear();

		$scope.properties = {
			'course': {
				name: 'Course',
				type: 'string',
				relationships: {
					'is equal to': {
						type: 'select',
						url: '/api/courses'
					},
					'contains': {
						type: 'text'
					}
				}
			},
			'grad_year': {
				name: 'Graduation Year',
				type: 'number',
				relationships: {
					'is equal to': {
						type: 'select',
						options: range(year + 4, 1950)
					},
					'is between': {
						type: 'range',
						options: [range(year + 4, 1950), range(year + 4, 1950)]
					}
				}
			},
			'group_member': {
				name: 'Group member',
				type: 'string',
				relationships: {
					'belonging to': {
						type: 'select',
						url: '/api/groups'
					}
				}
			}
		};

		$scope.group.criteria = [{
			property: '',
			verb: '',
			value: undefined
		}];

		$scope.valueChanged = function() {
			$http.post('/api/people/filter', {
				criteria: $scope.group.criteria
			}).success(function(data) {
				$scope.group.people = data.data;
			}).error(function(data) {
				console.log("Error:", data);
			});
		};

		var promises = {};

		$scope.selectOptionsForUrl = function(url) {
			return {
				placeholder: 'Value',
				query: function(query) {
					if (!promises[url]) {
						promises[url] = $http.get(url);
					}
					
					promises[url].success(function(data) {
						var loweredTerm = query.term.toLowerCase();
						query.callback({
							results: data.data.filter(function(obj) {
								return Object.keys(obj).map(function(k) { return obj[k] }).join(' ').toLowerCase().indexOf(loweredTerm) !== -1;
							}), 
							more: false
						});
					}).error(function(data) {
						query.callback({results: [], more: false});
					});
				},
				formatResult: function(course) {
					return course.name;
				},
				formatSelection: function(course) {
					return course.name;
				},
				createSearchChoice: function(term) {
					console.log(term);
				}
			}
		};

		// $scope.propertyChange = function(idx) {
		// 	for (var i = 0; i < $scope.properties.length; i++) {
		// 		if ($scope.properties[i].value == $scope.group.criteria[idx].property) {
		// 			$scope.group.criteria[idx].object = $scope.properties[i];
		// 			break;
		// 		}
		// 	}
		// };

		$scope.addCriterion = function(idx) {
			$scope.group.criteria.splice(idx + 1, 0, {property: '', verb: '', value: undefined});
		};

		$scope.deleteCriterion = function(idx) {
			$scope.group.criteria.splice(idx, 1);
			if ($scope.group.criteria.length == 0) {
				$scope.group.criteria = [{
					property: '',
					verb: '',
					value: undefined
				}]
			}
		};

		$scope.group.people = [];

		$scope.addPeopleSelectOptions = {
			placeholder: 'Search for people',
			multiple: true,
			id: function(person){
				return person.id;
			},
			ajax: {
				url: '/api/people',
				dataType: 'json',
				data: function(term, page){
					return {
						search: term,
						offset: (page - 1)*20,
						limit: 20
					};
				},
				results: function(data, page) {
					return {
						results: data.data.sort(function(a,b) {
							if (a.last_name < b.last_name) {
								return -1;
							} else if (a.last_name > b.last_name) {
								return 1;
							} else if (a.first_name > b.first_name) {
								return -1;
							} else if (a.first_name < b.first_name) {
								return 1;
							} else {
								return 0;
							}
						})
					};
				}
			},
			formatResult: function(person) {
				return person.last_name + ', ' + person.first_name;
			},
			formatSelection: function(person) {
				// console.log(person);
				return person.last_name + ', ' + person.first_name;
			},
		};

		$scope.done = function() {
			var groupData = angular.copy($scope.group);
			if (!$scope.group.is_smart) {
				delete(groupData.criteria);
			} else {
				delete(groupData.people);

				// Stringify criteria
				groupData.criteria = JSON.stringify(groupData.criteria);
			}

			GroupService.addGroup(groupData).success(function(returnData) {
				$modalInstance.close(returnData);
			}).error(function(returnData) {
				console.log("Error:", returnData);
			});
		};

		$scope.cancel = function() {
			$modalInstance.dismiss('cancel');
		};
	}
]);