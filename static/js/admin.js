function validatePrivateArea() {
    var valid = true;
    var privateAreaName = $("#privateAreaName").val();   
    var re=new RegExp('[0-9A-Za-z._-]{0,100}'); 
    if (privateAreaName.length >= 100) {
        dialogAlert('#privateAreaDialog','Please do not exceed maximum length for Private Area Name (100 characters)');
        valid = false;
    }       
    if (re.exec(privateAreaName) != privateAreaName) {
        dialogAlert('#privateAreaDialog','The only characters allowed are alphanumeric and . - _');
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
    var userElems = $('[name=userRow]');
    var users = [];
        
    for(var i = 0; i < userElems.length; i++){
        u = $(userElems[i])
        if (u.data('privateArea') || u.data('clear') ) {
            if (u.data('clear') == true) {
                newPrivateArea = ''
            } else {
                newPrivateArea = u.data('privateArea')                
            }
            user = {
                'newPrivateArea':newPrivateArea,
                'url':u.data('url')
            };
            users.push(user);            
        }
    }
    return users;
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
            success: function(data){
    			obj = JSON.parse(data);
    			if (obj.result == true) { 
                    showSuccessAlert('Private areas for users have been saved successfully')
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
        showAlert('No Private Areas to save');
    }

    
}

function createPrivateArea() {
    if (validatePrivateArea()) {
        startSpinnerOnButton('#submit_createPrivateArea');
    	$.ajaxSetup({
    		url: "/admin",
    		global: false,
    		type: "POST",
    		data: {
    		    'action': 'createPrivateArea',
    			'privateAreaName': $("#privateAreaName").val()
    		},
    		success: function(data){
    			obj = JSON.parse(data);
    			if (obj.result == true) {                    
                    stopSpinnerOnButton('#submit_createPrivateArea', createPrivateArea);
                   
                   
                    $(".dropdown-menu:last-child",$("#userTable")).each(function(i, elem) {
                        lastLink = $("a", $(this).children().last());
                        newArea = "<li><a name=\"privateArea\" data-foruser=\""+ lastLink.data('foruser')+"\" tabindex=\"-1\" href=\"#\">" + obj.newNamespace + "</a></li>";
                        $(newArea).insertBefore($(this).children().first());
                    });
                    $('[name=privateArea]').click(function() {changePrivateAreaValue(this);});
        		    $("#privateAreaDialog").modal('hide');
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
            success: function(data){
    			obj = JSON.parse(data);
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
    
    $('#submit_createPrivateArea').click( createPrivateArea );
    $('#saveUsers').click( saveUsers );        
            
});
