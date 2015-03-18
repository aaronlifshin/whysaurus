$(document).ready(function() {
    // Try to load the URL
    var pointURL = $('#leftColumnPoint').data('waitingurl');
    
    // Load the point (at pointURL, write history, replace current entry)
    loadPoint(pointURL, true, true);    
});
