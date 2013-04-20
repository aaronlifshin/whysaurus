				var unlinkVisible = false;

				function toggleUnlink() {
					if ( unlinkVisible ) {
						$( ".navWhy" ).removeClass("ui-helper-hidden");
						$( ".navWhy" ).show();
						$( ".navWhy" ).button();
						$( ".unlinkbutton" ).addClass("ui-helper-hidden");
						$( ".ui-helper-hidden" ).hide();
						$("#unlinkToggle").html('<span class="ui-button-text">Unlink</span>');
						unlinkVisible = false;
					} else {
						$( ".navWhy" ).addClass("ui-helper-hidden");
						$( ".ui-helper-hidden" ).hide();
						$( ".unlinkbutton" ).removeClass("ui-helper-hidden");
						$( ".unlinkbutton" ).show();
						$( ".unlinkbutton" ).button();
						$("#unlinkToggle").html('<span class="ui-button-text">Done</span>');
						unlinkVisible = true;
					}
				}

				function callPointEdit(){
					var ed = tinyMCE.get('editor_editPointDialog');
				  var text = tinyMCE.activeEditor.getBody().textContent;
					$.ajaxSetup({
					   url: "/editPoint",
					   global: false,
					   type: "POST",
						 data: {
							'urlToEdit': pointURL,
							'content': ed.getContent(),
							'plainText':text.substring(0,250),
							'title': $('#title_editPointDialog').val(),
							'imageURL':$('#link_editPointDialog').val(),
              'imageAuthor':$('#author_editPointDialog').val(),
              'imageDescription': $('#description_editPointDialog').val()
							},
							success: function(data){
								var ed = tinyMCE.get('editor_editPointDialog');
							  obj = JSON.parse(data);
								$('.mainPointContent').html(ed.getContent());
								$('.mainPointTitle h1').html($('#title_editPointDialog').val());
								$('.mainPointVersion').html(obj.version);
								$('.mainPointAuthor').html(obj.author);
								$('.mainPointDateEdited').html(obj.dateEdited);
                if (obj.imageURL) {
                  $('.pointDisplay').attr('src', "//d3uk4hxxzbq81e.cloudfront.net/FullPoint-" + obj.imageURL)
                }
								$('.mainPointImageURL').html(obj.imageURL);
								$('.mainPointImageAuthor').html(obj.imageAuthor);
								$('.mainPointImageDescription').html(obj.imageDescription);
								$("#editPointDialog").modal('hide');
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
                                $('#supportingPoint_' + obj.pointURL).remove();
                                if ($("[id^=supportingPoint_]").length == 0 ) {
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
			/*
				function openEditPointDialog() {

					var dialogButtons = {};
					dialogButtons["Save Point"] = function() {

  					  $( this ).dialog( "close" );
				  };
					dialogButtons["Cancel"] = function() {
					  tinyMCE.get('editor_').setContent('');
    				$('textarea.titleEdit').val('');
					  $('input[name=imageURL]').val('');
            $('input[name=imageAuthor]').val('');
            $('input[name=imageDescription]').val('');
					  $( this ).dialog( "close" );
					};
					$( "#dialogForm" ).dialog({title:"Edit Point", buttons: dialogButtons}	);
					$( "#dialogForm" ).dialog( "open" );

				}
	      */
	      function upVoteToggle(turnOn) {
	        if (turnOn) {
  	        $( "#upVote").removeClass("inactiveVote");
            $( "#upVote").addClass("greenVote");
	        } else {
	          $( "#upVote").removeClass("greenVote");
            $( "#upVote").addClass("inactiveVote");
	        }
	      }
	      function downVoteToggle(turnOn) {
	        if (turnOn) {
	          $( "#downVote").removeClass("inactiveVote");
            $( "#downVote").addClass("redVote");
          } else {
            $( "#downVote").removeClass("redVote");
            $( "#downVote").addClass("inactiveVote");
          }
        }

				function updateVoteButtonLabels(newVote){
				  var downvoteLabel = $( "#downVote a" ).text();
				  var upvoteLabel = $( "#upVote a" ).text();
				  var bigScore = $( "#bigScore" ).text();

				  if (myVote == 0 && newVote == 1) {// UPVOTE
				    var newVal = parseInt(upvoteLabel) + 1;
            $( "#upVote a" ).text(newVal.toString());
            $( "#bigScore" ).text(parseInt(bigScore) + 1);
            upVoteToggle(true);
          } else if (myVote == 0 && newVote == -1) { // DOWNVOTE
            var newVal = parseInt(downvoteLabel) + 1;
            $( "#downVote a" ).text(newVal.toString());
            $( "#bigScore" ).text(parseInt(bigScore) - 1);
            downVoteToggle(true);
          } else if (myVote == 1  &&  newVote == 0) { // CANCEL UPVOTE
            var newVal = parseInt(upvoteLabel) - 1;
            $( "#upVote a" ).text(newVal.toString());
            $( "#bigScore" ).text(parseInt(bigScore) - 1);
            upVoteToggle(false);
          } else if (myVote == -1  &&  newVote == 0) { // CANCEL DOWNVOTE
            var newVal = parseInt(downvoteLabel) - 1;
            $( "#downVote a" ).text(newVal.toString());
            $( "#bigScore" ).text(parseInt(bigScore) + 1);
            downVoteToggle(false);
          } else if (myVote == -1  &&  newVote == 1) { // DOWN TO UP
            var newVal = parseInt(downvoteLabel) - 1;
            $( "#downVote a" ).text(newVal.toString());
            var newVal = parseInt(upvoteLabel) + 1;
            $( "#upVote a" ).text(newVal.toString());
            $( "#bigScore" ).text(parseInt(bigScore) + 2);
            downVoteToggle(false);
            upVoteToggle(true);
          } else if (myVote == 1  &&  newVote == -1) {// UP TO DOWN
            var newVal = parseInt(downvoteLabel) + 1;
            $( "#downVote a" ).text(newVal.toString());
            var newVal = parseInt(upvoteLabel) - 1;
            $( "#upVote a" ).text(newVal.toString());
            $( "#bigScore" ).text(parseInt(bigScore) - 2);
            upVoteToggle(false);
            downVoteToggle(true);
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

function make_this_show_login_dlg(button) {
  button.attr('href',"#loginDialog");
  button.attr('data-toggle',"modal");
}

function populateEditFields() {
  var ed = tinyMCE.get('editor_editPointDialog');

	$('#title_editPointDialog').val($('#pointSummary div.mainPointTitle').text());
  if (ed) {
	  ed.setContent($('#pointSummary .mainPointContent').html() );
	}
	$('#author_editPointDialog').val($('#pointSummary div.mainPointImageAuthor').text());
  $('#description_editPointDialog').val($('#pointSummary div.mainPointImageDescription').text());
  var url = $('#pointSummary div.mainPointImageURL').text();

  $('#link_editPointDialog').val(url);
  if(url !== '') {
    if(url.match("https?://")) {
      $('#editPointDialog .filepicker-placeholder').attr('src', url);
    } else {
      $('#editPointDialog .filepicker-placeholder').attr('src', '//d3uk4hxxzbq81e.cloudfront.net/SummaryMedium-'+url);
    }
  }

}

function toggleTabbedArea(selectedTab, tabbedAreaToShow) {
	$('.tab').removeClass('selectedTab');
	$(selectedTab).addClass('selectedTab');
	$('.tabbedArea').hide();
	$(tabbedAreaToShow).show();
}

$(document).ready(function() {
			$( "[name=linkSupportingPoint]" ).button();

      if (!loggedIn) {
        $( "[name=linkSupportingPoint]" ).attr('href',"#loginDialog");
        $( "[name=linkSupportingPoint]" ).attr('data-toggle',"modal");
        make_this_show_login_dlg($( "#unlinkToggle" ));
        make_this_show_login_dlg($( "#editPoint" ));
        make_this_show_login_dlg($( "#upVote" ));
        make_this_show_login_dlg($( "#downVote" ));
        make_this_show_login_dlg($( "#viewPointHistory" ));
      } else {
        $( "[name=linkSupportingPoint]" ).click(function() {
          var params = [];
          params["parentPointURL"] = pointURL;
          post_to_url("/selectSupportingPoint", params);
        });

        $( "#unlinkToggle" )
  				.button()
  				.click(function() {
  					toggleUnlink();
  				});

        $( "#editPoint" ).attr('href',"#editPointDialog");
        $( "#editPoint" ).attr('data-toggle',"modal");
        $( "#editPoint" ).on('click', function() {
          populateEditFields();
          $('#frm_editPointDialog .filepicker').bindFilepicker();
        });

			  $("#submit_editPointDialog").on('click', function(e) {
    		  callPointEdit();
    		});

    		$( "#upVote" ).click(function() {upVote();});
    			//$('#upVote').button({ icons: {primary: 'ui-icon-up', secondary: null}});

    		$( "#downVote" ).click(function() {
    			downVote();
    		});

      };

			$( ".whybutton" ).button();
			$( ".unlinkbutton" ).button();
			$( ".unlinkbutton" ).addClass("ui-helper-hidden");
			$( ".ui-helper-hidden" ).hide();
			//try{
				$( "#deletePoint" ).button();
			//} catch (e) {};

			/* Tabs for supporting points, comments, and history */

			// Beginning state
			$('.tabbedArea').hide(); $('#supportingPointsArea').show();

			$('#viewSupportingPoints').click(function() {
				toggleTabbedArea(this, "#supportingPointsArea");
			});

			$('#viewComments').click(function() {
				toggleTabbedArea(this, "#disqus_thread");
			});

			$('#viewPointHistory').click(function() {
				toggleTabbedArea(this, "#historyArea");
			});

});
