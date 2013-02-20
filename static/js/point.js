				var unlinkVisible = false;
				
				function toggleUnlink() {
					if ( unlinkVisible ) {
						$( ".whybutton" ).removeClass("ui-helper-hidden");
						$( ".whybutton" ).show();
						$( ".whybutton" ).button();
						$( ".unlinkbutton" ).addClass("ui-helper-hidden");						
						$( ".ui-helper-hidden" ).hide();
						$("#unlinkToggle").html('<span class="ui-button-text">Unlink</span>');
						unlinkVisible = false;			
					} else {
						$( ".whybutton" ).addClass("ui-helper-hidden");
						$( ".ui-helper-hidden" ).hide();
						$( ".unlinkbutton" ).removeClass("ui-helper-hidden");
						$( ".unlinkbutton" ).show();
						$( ".unlinkbutton" ).button();
						$("#unlinkToggle").html('<span class="ui-button-text">Done</span>');
						unlinkVisible = true;
					} 		
				}
				
				function callPointEdit(){
					var ed = tinyMCE.get('textEdit');
				  var text = tinyMCE.activeEditor.getBody().textContent;
					$.ajaxSetup({
					   url: "/editPoint",
					   global: false,
					   type: "POST",
						 data: {
							'urlToEdit': pointURL,
							'content': ed.getContent(),
							'plainText':text.substring(0,250),
							'title': $('textarea.titleEdit').val(),			
							'imageURL':$('input[name=imageURL]').val(),
              'imageAuthor':$('input[name=imageAuthor]').val(),
              'imageDescription': $('input[name=imageDescription]').val()			
							},
							success: function(data){ 
								var ed = tinyMCE.get('textEdit');
							  obj = JSON.parse(data);
								$('.mainPointContent').html(ed.getContent()); 
								$('.mainPointTitle').html($('textarea.titleEdit').val()); 
								$('.mainPointVersion').html(obj.version);
								$('.mainPointAuthor').html(obj.author);
								$('.mainPointDateEdited').html(obj.dateEdited);
								if ($('.pointDisplay')) {
									$('.pointDisplay').remove();
								}
								if (obj.imageURL) {
									newImageContent = '<img class="pointDisplay" src="' + obj.imageURL + '"\/>';
									$('.mainPointContent').after(newImageContent);
								}
								$('.mainPointImageURL').html(obj.imageURL);	
								$('.mainPointImageAuthor').html(obj.imageAuthor);	
								$('.mainPointImageDescription').html(obj.imageDescription);	
								}
					 });
					$.ajax();
						
				}

        	function supportingPointUnlink(supportingPointURL) {
  					$.ajaxSetup({
  					   url: "/unlinkPoint",
  					   global: false,
  					   type: "POST",
  						 data: {
  							'mainPointURL': pointURL,
  							'supportingPointURL': supportingPointURL
  							},
  							success: function(data){ 
                              obj = JSON.parse(data);
                              if (obj.result == true) {
                                $('#point_' + obj.pointURL).remove();
                                if ($("[id^=point_]").length == 0 ) {
                                  $("#zeroSupportingPoints").show();
                                  $("#nonzeroSupportingPoints").hide();
                                  $( "[name=linkSupportingPoint]" ).button();
                                }							  
                              } else {
                                alert(obj.result);
                              }
                            }
                        });
  					$.ajax();
  				}
			
				function openEditPointDialog() {
					var ed = tinyMCE.get('textEdit');
					$('textarea.titleEdit').val($('div.mainPointTitle').text());
					ed.setContent($('.mainPointContent').html() );
					$('input[name=imageURL]').val($('div.mainPointImageURL').text());
				  $('input[name=imageAuthor]').val($('div.mainPointImageAuthor').text());
			    $('input[name=imageDescription]').val($('div.mainPointImageDescription').text());
					var dialogButtons = {};
					dialogButtons["Save Point"] = function() {
 					  	callPointEdit();
  					  $( this ).dialog( "close" );
				  };
					dialogButtons["Cancel"] = function() {	$( this ).dialog( "close" );};
					$( "#dialogForm" ).dialog({title:"Edit Point", buttons: dialogButtons}	);
					$( "#dialogForm" ).dialog( "open" );				
				}				
	       		
				function updateVoteButtonLabels(newVote){
				  var downvoteLabel = $( "#downVote" ).button("option", "label");
				  var upvoteLabel = $( "#upVote" ).button("option", "label");
				            
				  if (myVote == 0 && newVote == 1) {// UPVOTE
				    var newVal = parseInt(upvoteLabel) + 1;
            $( "#upVote" ).button("option", "label", newVal.toString());    
          } else if (myVote == 0 && newVote == -1) { // DOWNVOTE   
            var newVal = parseInt(downvoteLabel) + 1;
            $( "#downVote" ).button("option", "label", newVal.toString());    
          } else if (myVote == 1  &&  newVote == 0) { // CANCEL UPVOTE
            var newVal = parseInt(upvoteLabel) - 1;
            $( "#upVote" ).button("option", "label", newVal.toString());    
          } else if (myVote == -1  &&  newVote == 0) { // CANCEL DOWNVOTE  
            var newVal = parseInt(downvoteLabel) - 1;
            $( "#downVote" ).button("option", "label", newVal.toString());    
          } else if (myVote == -1  &&  newVote == 1) { // DOWN TO UP
            var newVal = parseInt(downvoteLabel) - 1;
            $( "#downVote" ).button("option", "label", newVal.toString());
            var newVal = parseInt(upvoteLabel) + 1;
            $( "#upVote" ).button("option", "label", newVal.toString());            
          } else if (myVote == 1  &&  newVote == -1) {// UP TO DOWN
            var newVal = parseInt(downvoteLabel) + 1;
            $( "#downVote" ).button("option", "label", newVal.toString());
            var newVal = parseInt(upvoteLabel) - 1;
            $( "#upVote" ).button("option", "label", newVal.toString());
          }
          myVote = newVote;
				}
								
				function upVote() {
				  $.ajaxSetup({
					   url: "/vote",
					   global: false,
					   type: "POST",
						 data: {
							'vote': myVote == 1 ? 0 : 1,
							'pointURL': pointURL
							},
              success: function(data){ 
                obj = JSON.parse(data);
                if (obj.result == true) {
                  updateVoteButtonLabels(obj.newVote);
                } else {
                  alert('An error happened and your vote may not have counted. Try a page refresh?');
                }
              }
						});
						$.ajax();
				}
				
				function downVote() {
				  $.ajaxSetup({
					   url: "/vote",
					   global: false,
					   type: "POST",
						 data: {
							'vote': myVote == -1 ? 0 : -1,
							'pointURL': pointURL
							},
              success: function(data){ 
                obj = JSON.parse(data);
                if (obj.result == true) {
                  updateVoteButtonLabels(obj.newVote);
                } else {
                  alert('An error happened and your vote may not have counted. Try a page refresh?');
                }
              }
						});
						$.ajax();
				}
				
				function deletePoint(urlToDelete) {
    			$.ajaxSetup({
    			   url: "/deletePoint",
    			   global: false,
    			   type: "POST",
    				 data: {
    					'urlToDelete': urlToDelete
    					},
    					success: function(data){ 
                  obj = JSON.parse(data);
                  if (obj.result == true) {
      						  alert('Deleted point ' + obj.deletedURL);	
      						  window.location = "/";	  
                  } else {
                    alert(obj.error);
                  }
    						},
              error: function (xhr, ajaxOptions, thrownError) {
                alert('ERROR:' + xhr.status);
                alert(thrownError);
              }
    				});
    				$.ajax();
    		}


$(document).ready(function() {
			$( "[name=linkSupportingPoint]" ).button();
							
			$( "#unlinkToggle" )
				.button()
				.click(function() {
					toggleUnlink();
				});

			$( "#upVote" )
				.button()
				.click(function() {
					upVote();
				});
			$('#upVote').button({ icons: {primary: 'ui-icon-up', secondary: null}});

			$( "#downVote" )
				.button()
				.click(function() {
					downVote();
				});			
			$('#downVote').button({ icons: {primary: 'ui-icon-down', secondary: null}});
			
			$( "#viewHistory" )
				.button()
				.click(function() {
					window.location.href="/pointHistory?pointUrl="+pointURL;
				});
					
			$( ".whybutton" ).button();
			$( ".unlinkbutton" ).button();
			$( ".unlinkbutton" ).addClass("ui-helper-hidden");
			$( ".ui-helper-hidden" ).hide();
			
			$( "#editPoint" )
				.button()
				.click(function() {
					openEditPointDialog();
				});
					
			//try{
				$( "#deletePoint" ).button();
			//} catch (e) {};
});