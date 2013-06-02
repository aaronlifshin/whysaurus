$(document).ready(function() {
  
  $( ".pointCard" ).click( function() {
    window.location.href=$(".navWhy", $(this)).attr('href');
    });
	
  $("[id^=point_HR_]").hover(function() {
      var pointCard = $(this);
      var borderWidth = pointCard.data('numsup') * 6;
      if (borderWidth > 0 ) {
          pointCard.css('border-left', "solid " + borderWidth.toString() + "px lightgray");  
          pointCard.css('border-right', "solid " + borderWidth.toString() + "px gray");  
          pointCard.css('border-top', "solid " + borderWidth.toString() + "px lightgray"); 
          pointCard.css('border-bottom', "solid " + borderWidth.toString() + "px gray"); 
      }  
  }, function() {
      var pointCard = $(this);
      var borderWidth = pointCard.data('numsup') * 6;
      if (borderWidth > 0 ) { // PUT EVERYTHING BACK!
          pointCard.css('border', "none");
      }
  });
		
});

