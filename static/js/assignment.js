function validateAssignment() {
    return true;
}

function getAssignmentData() {
    var titleArray = $('[name=documentControls] [name=documentTitle]').map(function(){
        return this.value;        
    });
    
    var contentArray = $('[name=documentControls] [name=documentContent]').map(function(){
        return this.value;        
    });
    
    var docArray = [];
    for (i = 0; i < titleArray.length; i += 1) {
        docArray.push({
            title: titleArray[i],
            content: contentArray[i]
        });
    };
    
    var aData = {
        title : $('#title').val(),
        summary: $('#summary').val(),
        directions: $('#directions').val(),
        teacherInstructions: $('#teacherInstructions').val(), 
        editKey:$('#editKey').val(),       
        documents: docArray
    };
    
    return aData;
}

function saveAssignment() {
    if (!validateAssignment()) {
        return;
    } else {
        var aData = getAssignmentData();
        startSpinnerOnButton('#saveAssignment');        
    	$.ajaxSetup({
    		url: "/assignment",
    		global: false,
    		type: "POST",
    		data: {
    		    'action': 'saveAssignment',
    			'assignmentData': JSON.stringify(aData)
    		},
            success: function(obj){
    			if (obj.result == true) { 
                    showSuccessAlert('Assignment Saved Successfully')
                    stopSpinnerOnButton('#saveUsers', saveAssignment);                
    			} else {
    				if (obj.error) {
    		    		showAlert(obj.error);
    		    	} else {
    		    		showAlert("There was an error");
    		    	}
                    stopSpinnerOnButton('#saveAssignment', saveAssignment);
    			}
    		},
    		error: function(xhr, textStatus, error){
                showAlert('The server returned an error. You may try again. ' + error);
                stopSpinnerOnButton('#saveAssignment', saveAssignment);
            }
    	});
    	$.ajax();
    }    
}

$(document).ready(function() {
    $('#addAnotherDocument').click(function() {
        var lastExistingDocument = $('[name="documentControls"]').last();
        var newDocumentRow = lastExistingDocument.clone();
        var rowNumber = $(lastExistingDocument).data('documentnumber') + 1;
        $('[name="documentNumber"]', newDocumentRow).text(rowNumber.toString());
        lastExistingDocument.after(newDocumentRow); 
        $(newDocumentRow).data('documentnumber', rowNumber);
        
    });
    $('#saveAssignment').click(saveAssignment);
});
