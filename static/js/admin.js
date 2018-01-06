function validatePrivateArea() {
    var valid = true;
    var privateAreaName = $("#privateAreaName").val();   
    var re=new RegExp('[0-9A-Za-z._-]+');
    if (privateAreaName.length >= 100) {
        dialogAlert('#privateAreaDialog','Private Area Name needs to be shorter (100 characters)');
        valid = false;
    }       
    if (re.exec(privateAreaName) != privateAreaName) {
        dialogAlert('#privateAreaDialog','The allowed characters are A-Z, a-z, 0-9, and period (.), dash (-) and underscore (_)');
        valid = false;
    }
    return valid;
}

function PAstartSpinner() {
    $('#submit_createPrivateArea').off('click');
    $('#submit_createPrivateArea').hide();
    $('#submit_createPrivateArea').after("<img id=\"spinnerImage\" src=\"/static/img/ajax-loader.gif\"/>");
}

function PAstopSpinner() {
    $("#spinnerImage").remove();
    $('#submit_createPrivateArea').click( createPrivateArea );        
    $('#submit_createPrivateArea').show();
}

function getUsersData() {
    return $('[name=userRow]').map(function(){
        var $u = $(this);

        var privateAreas = $u.find('.private-area-chooser option:selected').map(function(){
            return this.value;
        });
        
        var roleSelect = $u.find('.role-chooser option:selected');
        var role = roleSelect[0].value;

        return {
            privateAreas: privateAreas.toArray(),
            role: role,
            url: $u.data('url')
        };
    }).toArray();
}

function saveUsers() {
    users = getUsersData();
    if (typeof users !== 'undefined' && users.length > 0) {
        startSpinnerOnButton('#saveUsers');
    	$.ajaxSetup({
    		url: "/admin",
    		global: false,
    		type: "POST",
    		data: {
    		    'action': 'saveUsers',
    			'newUserValues': JSON.stringify(users)
    		},
            success: function(obj){
    			if (obj.result == true) { 
                    showSuccessAlert('Classroom assignments and roles have been saved successfully')
                    stopSpinnerOnButton('#saveUsers', saveUsers);                
    			} else {
    				if (obj.error) {
    		    		showAlert(obj.error);
    		    	} else {
    		    		showAlert("There was an error");
    		    	}
                    stopSpinnerOnButton('#saveUsers', saveUsers);
    			}
    		},
    		error: function(xhr, textStatus, error){
                showAlert('The server returned an error. You may try again. ' + error);
                stopSpinnerOnButton('#saveUsers', saveUsers);
            }
    	});
    	$.ajax();
    } else {
        showAlert('No Classrooms to save');
    }

    
}

function createPrivateArea() {
    if (validatePrivateArea()) {
        startSpinnerOnButton('#submit_createPrivateArea');
        var privateAreaName = $("#privateAreaName").val();
        var privateAreaDisplayName = $("#privateAreaDisplayName").val();
    	$.ajaxSetup({
    		url: "/admin",
    		global: false,
    		type: "POST",
    		data: {
    		    'action': 'createPrivateArea',
            'privateAreaName': privateAreaName,
            'privateAreaDisplayName': privateAreaDisplayName
    		},
    		success: function(obj){
    			if (obj.result == true) {                    
                    stopSpinnerOnButton('#submit_createPrivateArea', createPrivateArea);
                   
                   
                    $(".dropdown-menu:last-child",$("#userTable")).each(function(i, elem) {
                        lastLink = $("a", $(this).children().last());
                        newArea = "<li><a name=\"privateArea\" data-foruser=\""+ lastLink.data('foruser')+"\" tabindex=\"-1\" href=\"#\">" + obj.newNamespace + "</a></li>";
                        $(newArea).insertBefore($(this).children().first());
                    });
                    $('[name=privateArea]').click(function() {changePrivateAreaValue(this);});
        		    $("#privateAreaDialog").modal('hide');
                var privateAreaURL= 'https://www.whysaurus.com/area/' + privateAreaName;
                showSuccessAlert('Classroom ' + privateAreaName + ' has been created successfully. Users can go to <a href=\'' + privateAreaURL + '\'>' + privateAreaURL + '</a> to create accounts within this classroom.' )                
    			} else {
    				if (obj.error) {
    		    		dialogAlert('#privateAreaDialog',obj.error);
    		    	} else {
    		    		dialogAlert('#privateAreaDialog',"There was an error");
    		    	}
                     stopSpinnerOnButton('#submit_createPrivateArea', createPrivateArea);
    			}
    		},
    		error: function(xhr, textStatus, error){
                dialogAlert('#privateAreaDialog','The server returned an error. You may try again.' + error);
                 stopSpinnerOnButton('#submit_createPrivateArea', createPrivateArea);
            }
    	});
    	$.ajax();    	
    }
}

function changePrivateAreaValue(clickedElem) {
    var userIndex =  $(clickedElem).data('foruser');
    var newVal = $(clickedElem).text();
    if (newVal == '-- SET TO NONE') {
        $(".dropdown-toggle", $('#'+ userIndex )).text('Select User Private Area');     
        $('#'+ userIndex ).removeData('privateArea');  
        $('#'+ userIndex ).data('clear',true);                    
             
    } else {
        $(".dropdown-toggle", $('#'+ userIndex )).text(newVal); 
        $('#'+ userIndex ).data('privateArea',newVal);  
    }
}   

function resetPassword(clickedElem) {
    var userURL =  $(clickedElem).data('userurl');
    var r = confirm("Change the password for user " + userURL + "?");
    if (r == true) {
        $.ajaxSetup({
    		url: "/resetPassword",
    		global: false,
    		type: "POST",
    		data: {
    		    'userurl': userURL
    		},
            success: function(obj){
    			if (obj.result == true) { 
                    showSuccessAlert('Changed password for user ' + obj.username + '. New password: ' + obj.password);                             
    			} else {
    				if (obj.error) {
    		    		showAlert(obj.error);
    		    	} else {
    		    		showAlert("There was an error");
    		    	}
    			}
    		},
    		error: function(xhr, textStatus, error){
                showAlert('The server returned an error. You may try again. ' + error);
            }
    	});
    	$.ajax();
    }
}

function setUserGaid(clickedElem) {
    var userURL =  $(clickedElem).data('userurl');
    var r = prompt("New GA Id for user " + userURL + "?");
    if (r == null || r == "") {
        confirm("GA Set Bypassed!")
        return;
    }

    {
        $.ajaxSetup({
    		url: "/setUserGaid",
    		global: false,
    		type: "POST",
    		data: {
    		    'userurl': userURL,
                'newGaid': r
    		},
            success: function(obj){
    			if (obj.result == true) {
                    showSuccessAlert('Changed GA Id for user ' + obj.username + '. New GA Id: ' + obj.newGaid);
    			} else {
    				if (obj.error) {
    		    		showAlert(obj.error);
    		    	} else {
    		    		showAlert("There was an error");
    		    	}
    			}
    		},
    		error: function(xhr, textStatus, error){
                showAlert('The server returned an error. You may try again. ' + error);
            }
    	});
    	$.ajax();
    }
}

function setupChosen() {
    $('.chosen-select').chosen().change(
      function(e, o){
        
      }
    );
}

$(document).ready(function() {
    $('[name=privateArea]').click(function() {
        changePrivateAreaValue(this);       
    });
    
    $('#createPrivateArea').click(function() {
        $("#privateAreaDialog").modal('show');        
    });
        
    $('[name=resetPassword]').click(function() {
        resetPassword(this);       
    });

    $('[name=setUserGaid]').click(function() {
        setUserGaid(this);
    });
    
    $('#submit_createPrivateArea').click( createPrivateArea );
    $('#saveUsers').click( saveUsers );        
    setupChosen();
});
