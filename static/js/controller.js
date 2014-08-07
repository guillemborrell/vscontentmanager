var taskApp = angular.module('taskApp', ['ngResource']);

function getParameterByName(name) {
    name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
        results = regex.exec(location.search);
    return results == null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}


taskApp.controller('userController', function($scope, $resource){
    $scope.userresource = $resource('/REST/user');
    $scope.subscriptionresource = $resource('/REST/subscription');
    $scope.groupresource = $resource('/REST/group');
    $scope.groups = []
    $scope.subscriptions = [];
    $scope.users = [];
    $scope.newusername = '';
    $scope.newuserpassword = '';
    $scope.newusersubscription = '';
    $scope.newusergroup = '';
    $scope.newsubscriptionname = '';
    $scope.newgroupname='';
    $scope.newsubscriptionlevel = 0;

    var datag = $scope.groupresource.get(function(){
	for (i in datag.data){
	    $scope.groups.push(datag.data[i]);
	}
    });    

    var datas = $scope.subscriptionresource.get(function(){
	for (i in datas.data){
	    $scope.subscriptions.push(datas.data[i]);
	}
    });
						   
    var datau = $scope.userresource.get(function(){
	for (i in datau.data){
	    $scope.users.push(datau.data[i]);
	}});

    $scope.postSubscription = function(){
	var data = $scope.subscriptionresource.save(
	    {"name": $scope.newsubscriptionname,
	     "level": $scope.newsubscriptionlevel}
	    )
	window.location.replace('/users');
    }

    $scope.postGroup = function(){
	var data = $scope.groupresource.save(
	    {"name": $scope.newgroupname}
	)
	window.location.replace('/users');
    }

    $scope.postUser = function(){
	var data = $scope.userresource.save(
	    {"name": $scope.newusername,
	     "password": $scope.newuserpassword,
	     "group": $scope.newusergroup,
	     "subscription": $scope.newusersubscription}
	    );
	window.location.replace('/users');
    }

    $scope.deleteUser = function(key){
	var ask = confirm("¿Seguro que queires borrarlo?");
	if (ask){
	    var data = $scope.userresource.remove(params={id: key});
	    window.location.replace('/users');
	}
    }   

    $scope.deleteGroup = function(key){
	var ask = confirm("¿Seguro que queires borrarlo?");
	if (ask){
	    var data = $scope.groupresource.remove(params={id: key});
	    window.location.replace('/users');
	}
    }   

}
		  );

taskApp.controller('assignController', function($scope, $resource) {
    $scope.task = getParameterByName('id');
    
}
		  );

taskApp.controller('activityController', function($scope, $resource) {
    $scope.taskresource = $resource("/REST/task");
    $scope.groupresource = $resource("/REST/group");
    $scope.tasks = [];

    var datat = $scope.taskresource.get(function(){
	for (i in datat.data){
	    $scope.tasks.push(datat.data[i]);
	}
    });

    var datag = $scope.groupresource.get(function(){
	for (i in datag.data){
	    $scope.groups.push(datag.data[i]);
	}
    });

    $scope.deletetask = function(task){
	var ask = confirm("¿Seguro que quieres borrar esta tarea?");
	if (ask){
	    var data = $scope.taskresource.remove(params={id: task});
	    window.location.replace('/activity');
	}
    }

    $scope.assigntask = function(task){
	window.location.replace('/assign?id='+task);
    };
	
});

taskApp.controller('createTask', function ($scope, $resource) {
    $scope.available_tasks = ['Test','Actividad','Pregunta'];
    $scope.type = '';
    $scope.question = {"name": "",
		       "question": "",
		       "answer": ""};
    $scope.activity = {"name":"",
		       "description":""};
    $scope.test = {"name": "",
		   "question_list": [{"question": "",
				      "choices": ["1", "2", "3", "4"],
				      "right": 1}
				    ]
		  };
    $scope.error = false;

    $scope.add_question_to_test = function(question_list){
	question_list.push({"question": "",
			    "choices": ["", "", "", ""],
			    "right": 0});
    }
    $scope.add_choice_to_question = function(choices){
	choices.push("");
    }
    $scope.remove_choice_from_question = function(choices){
	choices.pop();
    }
    $scope.taskresource = $resource("/REST/task");

    $scope.submit_question = function (){
	var data = $scope.taskresource.save(
	    {"kind": $scope.type,
	     "name": $scope.question.name,
	     "data": $scope.question}
	);
	window.location.replace('/activity');
    };

    $scope.submit_activity = function (){
	var data = $scope.taskresource.save(
	    {"kind": $scope.type,
	     "name": $scope.activity.name,
	     "data": $scope.activity}
	);
	window.location.replace('/activity');
    };
    $scope.submit_test = function (){
	var data = $scope.taskresource.save(
	    {"kind": $scope.type,
	     "name": $scope.test.name,
	     "data": $scope.test}
	);
	window.location.replace('/activity');
    };

}
		  );
