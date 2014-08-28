
var taskApp = angular.module('taskApp', ['ngResource','ui.bootstrap']);

function getParameterByName(name) {
    name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
        results = regex.exec(location.search);
    return results == null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}

taskApp.controller('messageController', function($scope, $resource){
    $scope.messageresource = $resource('REST/message');
    $scope.deleteMessage = function (key){
	var ask = confirm("¿Seguro que queires borrarlo?");
	if (ask){
	    var data = $scope.messageresource.remove(params={id: key});
	}
    }
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
    $scope.newsubscriptionstartpage = 'home';
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
	     "startpage": $scope.newsubscriptionstartpage,
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

    $scope.deleteUser = function(key,idx){
	var ask = confirm("¿Seguro que queires borrarlo?");
	if (ask){
	    var data = $scope.userresource.remove(params={id: key});
	    $scope.users.splice(idx,1);
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

taskApp.controller('assignmentController', function($scope, $resource){
    $scope.assignmentid = getParameterByName('id');
    $scope.assignmentresource = $resource("REST/assignment");
    $scope.thisassignment = {};

    var dataa = $scope.assignmentresource.get(function(){
	$scope.thisassignment = dataa.data;
    },params={id: task} )
}
		  );

taskApp.controller('assignController', function($scope, $resource) {
    $scope.task = getParameterByName('id');
    $scope.groupresource = $resource("/REST/group");
    $scope.assignmentresource = $resource("REST/assignment");
    $scope.groups = [];
    $scope.newgroup = '';
    $scope.start = new Date();
    $scope.due = new Date();
    $scope.duration_in_minutes = '';
    var datag = $scope.groupresource.get(function(){
	for (i in datag.data){
	    $scope.groups.push(datag.data[i]);
	}
    });
    $scope.postAssignment = function(){
	$scope.assignmentresource.save({
	    "task": $scope.task,
	    "group": $scope.newgroup,
	    "start": $scope.start.toUTCString(),
	    "due": $scope.due.toUTCString(),
	    "duration_in_minutes": $scope.duration_in_minutes}
				      )
	window.location.replace('/activity');
    };
    
}
		  );


taskApp.controller('activityController', function($scope, $resource) {
    $scope.taskresource = $resource("/REST/task");
    $scope.groupresource = $resource("/REST/group");
    $scope.assignmentresource = $resource("/REST/assignment");
    $scope.tasks = [];
    $scope.assignments = [];

    var datat = $scope.taskresource.get(function(){
	for (i in datat.data){
	    $scope.tasks.push(datat.data[i]);
	}
    });

    var dataa = $scope.assignmentresource.get(function(){
	for (i in dataa.data){
	    $scope.assignments.push(dataa.data[i]);
	    }
	}
					     );

    $scope.deletetask = function(task){
	var ask = confirm("¿Seguro que quieres borrar este ejercicio?");
	if (ask){
	    var data = $scope.taskresource.remove(params={id: task});
	    window.location.replace('/activity');
	}
    }

    $scope.assigntask = function(task){
	window.location.replace('/assign?id='+task);
    };

    $scope.deleteassignment = function(assignment,idx){
	var ask = confirm("Seguro que quieres borrar esta tarea?");
	if (ask){
	    var data = $scope.assignmentresource.remove(params={id: assignment});
	    $scope.assignments.splice(idx,1);
	}
    };

    $scope.reviewAssignment = function(assignment){
	window.location.replace('/reviewassignment?id='+assignment);
    };
}
		  );

taskApp.controller('taskController', function ($scope, $resource) {
    $scope.subscriptionresource = $resource('/REST/subscription');
    $scope.subscription = '';
    var datas = $scope.subscriptionresource.get(function (){
	$scope.subscriptions = datas.data;
    }
					       );
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
	     "subscription": $scope.subscription,
	     "data": $scope.question}
	);
	window.location.replace('/activity');
    };

    $scope.submit_activity = function (){
	var data = $scope.taskresource.save(
	    {"kind": $scope.type,
	     "name": $scope.activity.name,
	     "subscription": $scope.subscription,
	     "data": $scope.activity}
	);
	window.location.replace('/activity');
    };
    $scope.submit_test = function (){
	var data = $scope.taskresource.save(
	    {"kind": $scope.type,
	     "name": $scope.test.name,
	     "subscription": $scope.subscription,
	     "data": $scope.test}
	);
	window.location.replace('/activity');
    };

}
		  );


taskApp.controller('viewTaskController', function ($scope, $resource) {
    $scope.taskid = getParameterByName('id');
    $scope.subscriptionresource = $resource('/REST/subscription');
    $scope.taskresource = $resource("/REST/task");
    $scope.available_tasks = ['Test','Actividad','Pregunta'];
    
    var datat = $scope.taskresource.get(
	{id: $scope.taskid},
	function() {
	    $scope.type = datat.data.kind;
            $scope.subscription = datat.data.subscriptionid;
	    if ($scope.type == "Test"){
		$scope.test = datat.data.data;
	    }
	    if ($scope.type == "Actividad"){
		$scope.activity = datat.data.data;
	    }
	    if ($scope.type == "Pregunta"){
		$scope.question = datat.data.data;
	    }
	}
    );
    var datas = $scope.subscriptionresource.get(function (){
	$scope.subscriptions = datas.data;
    }
					       );    
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
    
    
    $scope.submit_question = function (){
	var data = $scope.taskresource.save(
	    params={id: $scope.taskid},
	    {"kind": $scope.type,
	     "name": $scope.question.name,
	     "subscription": $scope.subscription,
	     "data": $scope.question}
	);
	window.location.replace('/activity');
    };
    
    $scope.submit_activity = function (){
	var data = $scope.taskresource.save(
	    params={id: $scope.taskid},
	    {"kind": $scope.type,
	     "name": $scope.activity.name,
	     "subscription": $scope.subscription,
	     "data": $scope.activity}
	);
	window.location.replace('/activity');
    };
    $scope.submit_test = function (){
	var data = $scope.taskresource.save(
	    params={id: $scope.taskid},
	    {"kind": $scope.type,
	     "name": $scope.test.name,
	     "subscription": $scope.subscription,
	     "data": $scope.test}
	);
	window.location.replace('/activity');
    };
    
}
		  );


taskApp.controller('makeAssignmentController', function ($scope, $resource) {
    $scope.assignmentid = getParameterByName('id');
    $scope.asgmtresource = $resource("/REST/makeassignment");
    $scope.taskresource = $resource("/REST/task");
    $scope.assignment = {};
    $scope.results = {};

    var dataa = $scope.asgmtresource.get(
	{id: $scope.assignmentid},function() {
	    $scope.assignment = dataa.data;
	    var datat = $scope.taskresource.get(
		{id: $scope.assignment.taskid}, function() {
		    $scope.results = datat.data;
		    
		    if ($scope.results.kind == 'Test'){
			for (i in $scope.results.data.question_list){
			    $scope.results.data.question_list[i].result = 1;
			}
		    }
		    if ($scope.results.kind == 'Pregunta'){
			$scope.results.result = '';
		    }
		}
	    );
	}
    );

    $scope.sendAssignment = function() {
	var data = $scope.asgmtresource.save(
	    params = {id: $scope.assignmentid},
	    {"data": $scope.results});

	window.location.replace('/app/home');
    }
}
		  );



taskApp.controller('reviseAssignmentController', function ($scope, $resource) {
    $scope.assignmentid = getParameterByName('id');
    $scope.asgmtresource = $resource("/REST/assignment");
    $scope.assignment = {};

    var dataa = $scope.asgmtresource.get(
	{id: $scope.assignmentid},function() {
	    $scope.assignment = dataa.data;
	}
    );

    $scope.done = function(){
	window.location.replace('/activity');
    }
}
		  );


