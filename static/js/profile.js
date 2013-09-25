function profileDialogAlert(alertHTML) {
    dialogAlert('#profileDialog', alertHTML);
}

function validateProfileDialog() {
    valid = true;
    //userName = $("#userName").val();    
    websiteVal = $("#userWebsite").val();
    areasVal = $("#userAreas").val();
    professionVal = $("#userProfession").val();
    bioVal = $("#userBio").val();
    /*if (userName.length >= 500) {
        profileDialogAlert('Please do not exceed maximum length for Username (500 characters)');
        valid = false;
    } */
    if (professionVal.length >= 500) {
        profileDialogAlert('Please do not exceed maximum length for Current Profession (500 characters)');
        valid = false;        
    }  
    if (websiteVal.length >= 500) {
        profileDialogAlert('Please do not exceed maximum length for Website URL (500 characters)');
        valid = false;        
    }  
    if (areasVal.length >= 500) {
        profileDialogAlert('Please do not exceed maximum length for Areas of Expertise (500 characters).  Wow, you must have a lot of expertise!');
        valid = false;        
    } 
    if (bioVal.length >= 500) {
        profileDialogAlert('Please do not exceed maximum length for Username (500 characters)');
        valid = false;
    }
    if (websiteVal != '' && !validateURL(websiteVal)) {
        profileDialogAlert('The URL you specified does not look like a valid URL');
        valid = false;
    }
    return valid;
}

function saveProfileInfo() {
    if (validateProfileDialog()) $('#frm_profileDialog').submit();
}

$(document).ready(function() {

    // Beginning state for the TABBED AREAS
    $('.tabbedArea').hide(); 
    if (viewingOwnPage) {
        $('#notificationsArea').show();    
        $('#notificationView').click(function() {
           toggleTabbedArea(this, "#notificationsArea");
        });             
    } else {
        $('#createdPointsArea').show();                
    }

    $('#createdPoints').click(function() {
        toggleTabbedArea(this, "#createdPointsArea");
    });

    $('#editedPoints').click(function() {
        toggleTabbedArea(this, "#editedPointsArea");
    });
    
    $('#editButton').click(function() {
        $("#profileDialog").modal('show');        
    });
    
    $('[name=profileEdit]').click(function() {
        $("#profileDialog").modal('show');        
    });
    
    $('#submit_profileDialog').click( saveProfileInfo );        
});