function validatePasswordChange() {
    valid = true;
    password1 = $("#password1").val();    
    password2 = $("#password2").val();    

    if (password1 != password2) {
        showAlert('Oops. Your passwords do not match.');
        valid = false;
    } else if (password1.length < 8) {
        showAlert('Please make your password 8 or more characters in length.');
        valid = false;
    } else if (!validatePassword(password1)) {
        showAlert('Please include  at least one letter and at least one number in your passoword.');
        valid = false;
    }
    return valid;
    
}
