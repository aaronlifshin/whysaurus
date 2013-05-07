
	function selectPoint(pointUrl, parentPointUrl){
	  	$.ajaxSetup({
			url: "/linkPoint",
			global: false,
			type: "POST",
		 	data: {
				'supportingPointURL': pointUrl,
				'parentPointURL': parentPointUrl
				},
			success: function(data){
			  obj = JSON.parse(data);
			  if (obj.result == true) {
				window.location.href="/point/" + parentPointURL;
			  } else {
			  	if (obj.error) {
			    	alert(obj.error);
			    } else {
			    	alert("There was an error");
			    }
			  }
			}
		});
		$.ajax();
	}

	function addPoint(){
	    if ($('#title_createSupportingPoint').val().length > MAX_TITLE_CHARS) {
            alert('Too many characters in the title');
            return;
        }
		var ed = tinyMCE.get('editor_createSupportingPoint');
        var text = tinyMCE.activeEditor.getBody().textContent;
        $("#submit_createSupportingPoint").off('click');
        $("#submit_createSupportingPoint").hide();
        $("#submit_createSupportingPoint").after("<img id=\"spinnerImage\" src=\"/static/img/ajax-loader.gif\"/>");
		$.ajaxSetup({
			url: "/addSupportingPoint",
			global: false,
			type: "POST",
			data: {
				'content': ed.getContent(),
                'plainText': text.substring(0,500),
				'title': $('#title_createSupportingPoint').val(),
				'pointUrl': parentPointURL,
				'imageURL':$('#link_createSupportingPoint').val(),
                'imageAuthor':$('#author_createSupportingPoint').val(),
                'imageDescription': $('#description_createSupportingPoint').val()
			},
			success: function(data){
				obj = JSON.parse(data);
				if (obj.result == true) {
				    window.location.href="/point/" + parentPointURL;
				} else {
					if (obj.error) {
			    		alert(obj.error);
			    	} else {
			    		alert("There was an error");
			    	}
                    $("#spinnerImage").remove();
				    $("#submit_createSupportingPoint").on('click', function(e){addPoint();}); 
				    $("#submit_createSupportingPoint").show();
				}
 			},
 			error: function(xhr, textStatus, error){
                alert('The server returned an error. You may try again.');
                $("#spinnerImage").remove();
                $("#submit_createSupportingPoint").on('click', function(e){addPoint();}); 
                $("#submit_createSupportingPoint").show();                			    
            } 			
		});
		$.ajax();
	}

function hideSpinner() {
    $("#spinnerImage").hide();
}

function setUpSelectPointButtons() {
    $("[id^=selectPoint_div_]").on('click', function(e){
        var theLink = $(this);
        selectPoint(theLink.data('pointurl'), parentPointURL );
    });
}

function setUpPopoutButtons() {
    $("[id^=popoutPoint_]").on('click', function(e){
        var theLink = $(this);
        window.open( "/point/" + theLink.data('pointurl'),theLink.data('pointtitle') , "height=800,width=1000");
    }); 
}

$(document).ready(function() {
  if (!loggedIn) {
    $( "#createSupportingPointLink" ).attr('href',"#loginDialog");
    $( "#createSupportingPointLink" ).attr('data-toggle',"modal");
  } else {
    $( "#createSupportingPointLink" ).attr('href',"#createSupportingPoint");
    $( "#createSupportingPointLink" ).attr('data-toggle',"modal");
    $("#submit_createSupportingPoint").on('click', function(e){addPoint();});
    setUpSelectPointButtons();
  }
  setUpPopoutButtons();
  
	$(".searchBox", $(".searchColumn")).keyup(function(event){
		if(event.keyCode == 13){
			$.ajaxSetup({
				url: "/ajaxSearch",
				global: false,
				type: "POST",
				data: {
					'searchTerms': $(".searchBox").val(),
					'exclude' : parentPointURL
				},
				success: function(data){
					$("[id^=searchPoint]",$(".searchColumn")).remove();
					obj = JSON.parse(data);
					if (obj.result == true) {
						appendAfter = $(".searchColumn");
						for(var i=0; i < obj.searchResults.length; i++){						    
							var oneResult = obj.searchResults[i];
							// we need to create 4 divs
							// 1. a row-fluid
							mainRowDiv = $('<div/>', { class:"row-fluid", id:"searchPoint_"+oneResult['url']});							
							// 2. the popout
							popOutDiv = $('<div/>', {class:"span1 noRightChannel"});
							popOutDiv.html("<a id=\"popoutPoint_" + oneResult['url'] +
							                "\" data-pointurl=\""+ oneResult['url']  +
							                "\" data-pointtitle=\"" + oneResult['title'] + "\" ></a>");                            
							// 3. the select supporting point div
							if (oneResult['voteTotal'] >= thresholdGreen ) {spanClass = 'green'; } 
							else if  (oneResult['voteTotal'] <= thresholdRed) { spanClass = 'red'; } 
							else {  spanClass = 'yellow'; }
							
							selectDiv = jQuery('<div/>', {
								class: "pointSmall span11 " + spanClass,
								id: "selectPoint_div_search_" +  oneResult['url'],
								alt: "Use " + oneResult['url']								
								});
							selectDiv.data('pointurl', oneResult['url']);
							// 4. and, inside it, the score and title div and the arrow div
							titleDiv = jQuery('<div/>',{class:"span10 title"} );
							titleDiv.html("<h5><span class=\"score\">" + oneResult['voteTotal'] + 
							              "</span> <a href=\"#\" > " + oneResult['title'] + "</a></H5>");
							
							buttonDiv= jQuery('<div/>',{class:"span2"} );
                            buttonDiv.html("<a class=\"pull-right\" href=\"#\"id=\"selectPoint_arrow_" + 
                                            oneResult['url'] + "\"alt=\"Use " + oneResult['title'] + "\" ></a>");

                            selectDiv.append(titleDiv);
                            selectDiv.append(buttonDiv);
                            mainRowDiv.append(popOutDiv);
                            mainRowDiv.append(selectDiv);							
							appendAfter.append(mainRowDiv);
							mainRowDiv.show();
			        	}
                        setUpSelectPointButtons();
                        setUpPopoutButtons();
					} else {
						alert('There were no results for: ' + $(".searchBox").val() + ' or that is already a supporting point');
					}
	 			}
			});
			$.ajax();
	  }
	});
});
