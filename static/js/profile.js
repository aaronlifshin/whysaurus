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
    email = $("#userEmail").val();
    notificationFrequency = $('input[type="radio"]:checked').val();
    
    if (email.trim() != "" && !validateEmail(email)) {
        profileDialogAlert('That doesn\'t look like a valid email address.');
        valid = false;  
    }
    
    if (notificationFrequency != 'Never' && email.trim() == "" ) {
        profileDialogAlert('Please supply an email address if you wish to receive ' + notificationFrequency + ' notifications.');
        valid = false;  
    } 
    
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
           toggleTabbedArea("#profileTabbedArea", this, "#notificationsArea");
        });             
    } else {
        $('#createdPointsArea').show();                
    }

    $('#createdPoints').click(function() {
        toggleTabbedArea("#profileTabbedArea", this, "#createdPointsArea");
    });

    $('#editedPoints').click(function() {
        toggleTabbedArea("#profileTabbedArea", this, "#editedPointsArea");
    });
        
    $('[name=profileEdit]').click(function() {
        $("#profileDialog").modal('show');        
    });
    
    $('#submit_profileDialog').click( saveProfileInfo );    
    
    $('input:radio').screwDefaultButtons({
            image: 'url("/static/img/screwdefault_radio_design_roSpinner.gif")',
            width: 45,
            height: 45
    });    
});