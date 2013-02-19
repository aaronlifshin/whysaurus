
	
	function checkPointContent(content) {
	  var result = "";
	  var firstImage = content.indexOf("<img");
	  if (firstImage == 0) {
	    result = "";
	  } else if (firstImage > 4) {
	    result = "Images must be placed at the beginning of the point."
    } else {
	    var secondImage = content.indexOf("<img", firstImage+1);
	    if (secondImage > 0) {
        result = "Cannot have more than one image in the point."
	    }
	  }
	  return result;
	}
	
	function getWindowHeight() {
		  var height;

      if (typeof(window.innerHeight) == "number") //non-IE
          height = window.innerHeight;
      else if (document.documentElement && document.documentElement.clientHeight) //IE 6+ strict mode
          height = document.documentElement.clientHeight;
      else if (document.body && document.body.clientHeight) //IE 4 compatible / IE quirks mode
          height = document.body.clientHeight;
          
      return height;
		}
		function toDialogFormHeight(id, minus) {
        var height;
        height = $(this).height( $('#dialogForm').closest('.ui-dialog').height());
        if (document.getElementById(id)) {
        	document.getElementById(id).style.height = (height - minus) + "px";
        }           
    }   
    
    function positionEditDialog(diff) {
      element = $("#dialogForm");
      element.dialog('option', 'height', getWindowHeight() * .9);
      element.dialog('option', 'width', $(window).width()*.7);
      element.dialog('option', 'position', 'center');
      toDialogFormHeight('frmEditFields', diff);
      toDialogFormHeight('editFields', diff);
      toDialogFormHeight('textEdit_tbl', diff);
      toDialogFormHeight('textEdit_ifr', diff);
    }
  	
		function newPoint() {
			var ed = tinyMCE.get('textEdit');
			$.ajaxSetup({
				   url: "/newPoint",
			   global: false,
			   type: "POST",
				 data: {
					'content': ed.getContent(),
					'title': $('textarea.titleEdit').val(),			
					'imageURL':$('input[name=imageURL]').val(),
          'imageAuthor':$('input[name=imageAuthor]').val(),
          'imageDescription': $('input[name=imageDescription]').val()			
					},
          success: function(data){ 
            var ed = tinyMCE.get('textEdit');	
            // Data comes as ready HTML to be inserted 
            $(data).insertAfter($('.preamble'));
      			$( "[id^=editPoint]" ).button();
						// $( "[id^=deletePoint]" ).button();
      			$('textarea.titleEdit').val('');
  					ed.setContent("");
  					$('input[name=imageURL]').val('');
  				  $('input[name=imageAuthor]').val('');
  			    $('input[name=imageDescription]').val('');
          }
				});
				$.ajax();
		}
				
		function openNewPointDialog() {	
	        document.getElementById("textEdit_tbl").style.width='100%';
	        document.getElementById("textEdit_ifr").style.width='100%';
	        document.getElementById("textEdit_tbl").style.height='100%';
	        document.getElementById("textEdit_ifr").style.height='100%';
			var dialogButtons = {};
			dialogButtons["Create Point"] = function() {
			  var checkContentError = checkPointContent(tinyMCE.get('textEdit').getContent());
			  if (checkContentError != "") {
			    alert(checkContentError);
			  } else {
			  newPoint();
			  $( this ).dialog( "close" )
			  }
			};
			
			dialogButtons["Cancel"] = function() {	
			  var edSummary = tinyMCE.get('textEdit');
				edSummary.setContent('');
				$('textarea.titleEdit').val('');
			  $( this ).dialog( "close" );
		  	};
		  	
			$( "#dialogForm" ).dialog({title:"New Point", buttons: dialogButtons});
			$( "#dialogForm" ).dialog( "open" );
		}

function showCreatePoint() {
	$("#CreatePoint").css('visibility','visible');;
} 

  $(document).ready(function() { 
     tinyMCE.init({
      // General options
      mode : "specific_textareas",
      theme : "advanced",
      editor_selector : "mceEditor",
      editor_deselector : "mceNoEditor",
      paste_text_sticky: true,
      paste_text_sticky_default: true,
      plugins : "autolink,lists,spellchecker,iespell,inlinepopups,noneditable,paste",
      // Theme options
      theme_advanced_buttons1 : "bold,italic,underline,|,sub,sup,bullist,numlist,blockquote,|,undo,redo,|,link,unlink,code,spellchecker",
      theme_advanced_buttons2 : "",
      theme_advanced_buttons3 : "",
      theme_advanced_buttons4 : "",
      theme_advanced_toolbar_location : "top",
      theme_advanced_toolbar_align : "left",
      theme_advanced_statusbar_location : "bottom",
      theme_advanced_resizing : false,
      // Skin options
      skin : "o2k7",
      skin_variant : "silver", 
      // Drop lists for link/image/media/template dialogs
      template_external_list_url : "js/template_list.js",
      external_link_list_url : "js/link_list.js",
      external_image_list_url : "js/image_list.js",
      media_external_list_url : "js/media_list.js"
    });
    
    
	$(".searchBox", $(".searchArea")).keyup(function(event){
    if(event.keyCode == 13){
        window.location.href="/search?searchTerms="+$(".searchBox", $(".searchArea")).val();
    }
	});
	
	
	// Index page stuff
	$( "#CreatePoint" ).click(function() {
			openNewPointDialog();
	});

	$( "[id^=deletePoint]" ).button();
	$( "[id^=editPoint]" ).button();
	$(" input:submit" ).button();
  
    // Dialog form handling
	$("#dialogForm").dialog({
		autoOpen: false,
		height: getWindowHeight() * .9,
		width: $(window).width()*.7,
		modal: true
	});			

  window.onload = function() {positionEditDialog(500); };
  window.onresize = function() {positionEditDialog(500); };
});

	