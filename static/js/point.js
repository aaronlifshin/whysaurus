

function searchDialogAlert(alertHTML) {
    $('#linkedPointSearchDialog #alertArea').html($('<div class="alert"><button type="button" class="close" data-dismiss="alert">&times;</button>' + alertHTML + '</div>'));
}

function toggleUnlink(elem, linkType) {
    
    unlinkVisible = $(elem).text() == 'Cancel';    
	if ( unlinkVisible ) {
	    // Hiding the unlink controls
	    $(elem).text('Unlink a Point');
	    $(".unlinkbutton", $('#' + linkType + '_nonzeroPoints')).remove();
        $( ".pointCard" ).unbind('mouseenter');
        $( ".pointCard" ).unbind('mouseleave');    
        $( ".pointCard" ).removeClass('redBorder');    
		
        makePointsCardsClickable();
            	    
	} else {	    
	    // Find all the point cards underneath my link type
	    pointCards = $('.pointCard', $('#' + linkType + '_nonzeroPoints'))	    
	    // Put the element on them each
	    pointCards.hover(
            function() {
                $(this).append(    
        	        "<div class='unlinkbutton'><a href='javascript:;' onclick='javascript:pointUnlink(this, \""+ 
        	        linkType +"\")' alt='Unlink " + linkType + " Point'>Unlink This Point</a></div>" );
            },
            function() {
                $(this).find('.unlinkbutton').remove();
            }
        );
		pointCards.addClass('redBorder');
	    pointCards.unbind('click');
	    $(elem).text('Cancel');
	}
}

function insertImage(imageURL, author, description) {
	if ($('#mainPointImageArea').length) {
	    $('.pointDisplay').attr('src', "//d38pzqn4b9ae2a.cloudfront.net/FullPoint-" + encodeURIComponent(imageURL))
		$('.mainPointImageURL').html(imageURL);
		$('.mainPointImageAuthor').html(author);
		$('.mainPointImageCaption').html(description);
	} else { // no image yet, insert the main point image area
		$('#pointSummary').after('<div id="mainPointImageArea" class="span3"> \
	            <img class="pointDisplay" src="' + '//d38pzqn4b9ae2a.cloudfront.net/FullPoint-' + encodeURIComponent(imageURL) +
				'" /><div class="mainPointImageCaption">' + description + '</div> \
	            <div class="mainPointImageAuthor">' + author + '</div> \
		    </div>');
		$('.mainPointImageURL').html(imageURL);					
	}
}

// updates the byline
function updateVersionHeader(authorURL, author, dateEdited) {
	
	// TO DO: insert code here to update the number of contributors in the byline
	
	// Old version:
	//$('.byline').html('<span class="contributor">Most Recent Contributor: </span>' + 
	//    '<a href=\'/user/' + authorURL +'\'>'+ author + '</a><br>Last Edited ' + dateEdited + 
	//    '. <a id="viewPointHistory">View History</a>');
    //$('#viewPointHistory').off('.ys').on('click.ys',viewPointHistory);
	
	console.log('ran updateVersionHeader ');	
}

function callPointEdit(){
    if ($('#title_pointDialog').val().length > MAX_TITLE_CHARS) {
        editDialogAlert('Please do not exceed 200 characters for the title.');
        return;
    }
    
    if ($('#title_pointDialog').val().length == "") {
        editDialogAlert('To create a point you must enter something for the title!');      
        return;
    }
    
    if (!addCurrentSource()) { return; }  
    
	var ed = tinyMCE.get('editor_pointDialog'); 
    var text = tinyMCE.activeEditor.getBody().textContent;
  
    
    disableButtonPrimary('#submit_pointDialog');
    $('#submit_pointDialog').text("Publish to Library...");
    $('#submit_pointDialog').after("<img id=\"spinnerImage\" class=\"spinnerPointSubmitButtonPosition\" src=\"/static/img/ajax-loader.gif\"/>");
	$.ajaxSetup({
	   url: "/editPoint",
	   global: false,
	   type: "POST",
		 data: {
			'urlToEdit': $('#pointArea').data('pointurl'),
			'content': ed.getContent(),
			'plainText':text.substring(0,250),
			'title': $('#title_pointDialog').val(),
			'imageURL':$('#link_pointDialog').val(),
            'imageAuthor':$('#author_pointDialog').val(),
            'imageDescription': $('#description_pointDialog').val(),
            'sourcesURLs': JSON.stringify(getNewSourcesURLs()),
            'sourcesNames': JSON.stringify(getNewSourcesNames()),
            'sourcesToRemove': JSON.stringify($('#pointDialog').data('sourcesToRemove'))
			},
			success: function(obj){
                if (obj.result) {
    				var ed = tinyMCE.get('editor_pointDialog');
    				$('.mainPointContent').html(ed.getContent());
    				$('#mainPointTitle').html($('#title_pointDialog').val());

                    // this refreshes the old header (time stamp, most recent contributor)
    				//updateVersionHeader(obj.authorURL, obj.author, obj.dateEdited);
				    
                    if (obj.imageURL) {
    					insertImage(obj.imageURL, obj.imageAuthor, obj.imageDescription);
    				}

    				$('#mainPointSources').remove();
    				$('[name=mainPointSource]').remove();				
    				$('.mainPointContent').after(obj.sourcesHTML);
    				$('#viewPointHistory').click(viewPointHistory);	
                	stopSpinner();
    				$("#pointDialog").modal('hide');
                    resetSubmitButton('#submit_pointDialog');
    				$('#pointArea').data('pointurl', obj.pointURL);			                
                } else {
                    editDialogAlert(obj.error);
                	stopSpinner();
                    resetSubmitButton('#submit_pointDialog');
                }
			},
     		error: function(xhr, textStatus, error){
                alert('The server returned an error. You may try again.');
            	stopSpinner();
                resetSubmitButton('#submit_pointDialog');
            }
	 });
	$.ajax();
}

function pointUnlink(elem, linkType) {
    
    startSpinnerOnButton(elem);

    pointCard = $(elem).closest('div.relevanceVote').next();    
    // previously:
    //pointCard = $(elem).closest('div.relevanceVote').next().children('.pointCard');
    
    supportingPointURL = pointCard.data('pointurl');
    pointURL = $('#pointArea').data('pointurl');
    //_gaq.push(['_trackEvent', 'Link Manipulation', 'Unlink ' + linkType , supportingPointURL + ' from ' + pointURL]);
    ga('send', 'event', 'Link Manipulation', 'Unlink ' + linkType, supportingPointURL + ' from ' + pointURL);
    
	$.ajaxSetup({
	   url: "/unlinkPoint",
	   global: false,
	   type: "POST",
		 data: {
			'mainPointURL': pointURL,
			'supportingPointURL': supportingPointURL,
			'linkType': linkType
			},
			success: function(obj){
				if (obj.result == true) {
                
                    // remove the relevanceArea for the point card                 
                    pointCard.prev('.relevanceVote').prev().remove();      
                    pointCard.prev('.relevanceVote').remove(); 
                    // previously:
                    //pointCard.parent().prev('.relevanceVote').prev().remove();      
                    //pointCard.parent().prev('.relevanceVote').remove();  
                    
					// remove the a link containing the point card
					pointCard.remove();
                    // previously:
					//pointCard.parent().remove();
                   
					if ($('.pointCard', $('#' + linkType + '_nonzeroPoints')).length == 0 ) {
						$("#" + linkType + "_zeroPoints").show();
						$("#" + linkType + "_nonzeroPoints").hide();
                        $("#" + linkType + "_nonzeroPointsFooter").addClass("hide");
                        
						$("[name=" + linkType + "_linkPoint]").button();                        
					} 
                    // no longer needed
                    //else {
						//setPointListHeader(linkType);
					//}
					//updateVersionHeader(obj.authorURL, obj.author, obj.dateEdited);
				} else {
					showErrorAlert('There was an error during unlinking: ' + obj.error); 
				}
			}
      });
	$.ajax();
}

// DEPRECATED
function upVoteToggle(turnOn) {
    if (turnOn) {
        $( "#upVote").removeClass("inactiveVote");
        $( "#upVote").addClass("greenVote");
    } else {
        $( "#upVote").removeClass("greenVote");
        $( "#upVote").addClass("inactiveVote");
    }
}
// DEPRECATED
function downVoteToggle(turnOn) {
    if (turnOn) {
        $( "#downVote").removeClass("inactiveVote");
        $( "#downVote").addClass("redVote");
    } else {
        $( "#downVote").removeClass("redVote");
        $( "#downVote").addClass("inactiveVote");
    }
}


// Deprecated, as separate counts are no longer shown
// Leaving it in here in case they come back
function updateVoteButtonLabelsOld(newVote){
    var downvoteLabel = $( "#downVoteStat" ).text();
    var upvoteLabel = $( "#upVoteStat" ).text();
    var voteTotal = $( "#voteTotal" ).text();
    myVote = $('#voteTotal').data('myvote');
    
    if (myVote == 0 && newVote == 1) {// UPVOTE
        var newVal = parseInt(upvoteLabel) + 1;
        $( "#upVoteStat" ).text(newVal.toString());
        $( "#voteTotal" ).text(parseInt(voteTotal) + 1);
        upVoteToggle(true);
    } else if (myVote == 0 && newVote == -1) { // DOWNVOTE
        var newVal = parseInt(downvoteLabel) + 1;
        $( "#downVoteStat" ).text(newVal.toString());
        $( "#voteTotal" ).text(parseInt(voteTotal) - 1);
        downVoteToggle(true);
    } else if (myVote == 1  &&  newVote == 0) { // CANCEL UPVOTE
        var newVal = parseInt(upvoteLabel) - 1;
        $( "#upVoteStat" ).text(newVal.toString());
        $( "#voteTotal" ).text(parseInt(voteTotal) - 1);
        upVoteToggle(false);
    } else if (myVote == -1  &&  newVote == 0) { // CANCEL DOWNVOTE
        var newVal = parseInt(downvoteLabel) - 1;
        $( "#downVoteStat" ).text(newVal.toString());
        $( "#voteTotal" ).text(parseInt(voteTotal) + 1);
        downVoteToggle(false);
    } else if (myVote == -1  &&  newVote == 1) { // DOWN TO UP
        var newVal = parseInt(downvoteLabel) - 1;
        $( "#downVoteStat" ).text(newVal.toString());
        var newVal = parseInt(upvoteLabel) + 1;
        $( "#upVoteStat" ).text(newVal.toString());
        $( "#voteTotal" ).text(parseInt(voteTotal) + 2);
        downVoteToggle(false);
        upVoteToggle(true);
    } else if (myVote == 1  &&  newVote == -1) {// UP TO DOWN
        var newVal = parseInt(downvoteLabel) + 1;
        $( "#downVoteStat" ).text(newVal.toString());
        var newVal = parseInt(upvoteLabel) - 1;
        $( "#upVoteStat" ).text(newVal.toString());
        $( "#voteTotal" ).text(parseInt(voteTotal) - 2);
        upVoteToggle(false);
        downVoteToggle(true);
    }
    $('#voteTotal').data('myvote', newVote);
}

function upVote() {    
    pointURL = $('#pointArea').data('pointurl');
    vote = $('#voteTotal').data('myvote') == 1 ? 0 : 1;
    //_gaq.push(['_trackEvent', 'Vote', 'Up', pointURL, vote]);
    ga('send', 'event', 'Vote', 'Up', pointURL, vote);
    
    $.ajaxSetup({
       url: "/vote",
       global: false,
       type: "POST",
       data: {
    		'vote': vote,
    		'pointURL': pointURL
    		},
       success: function(obj){
            if (obj.result == true) {
                updateVoteTotal(obj.newVote, $('#voteTotal'), $( "#upVote") , $( "#downVote"));
                updatePointScore(obj.newScore, $('#pointScoreSpan'));
            } else {
                alert('An error happened and your vote may not have counted. Try a page refresh?');
            }
        }
    });
    $.ajax();
}

function downVote() {
    pointURL = $('#pointArea').data('pointurl');
    vote = $('#voteTotal').data('myvote') == -1 ? 0 : -1;
    //_gaq.push(['_trackEvent', 'Vote', 'Down', pointURL, vote]);
    ga('send', 'event', 'Vote', 'Down', pointURL, vote);
    $.ajaxSetup({
        url: "/vote",
        global: false,
        type: "POST",
        data: {
    		'vote': vote,
    		'pointURL': pointURL
    		},
        success: function(obj){
            if (obj.result == true) {
                updateVoteTotal(obj.newVote, $('#voteTotal'), $( "#upVote"), $( "#downVote"));
                updatePointScore(obj.newScore, $('#pointScoreSpan'));
            } else {
                alert('An error happened and your vote may not have counted. Try a page refresh?');
            }
        }
    });
    $.ajax();
}

function changeRibbon() {
    var newRibbonValue = !$("#blueRibbon").data("ribbonvalue"); // "false" -> true
    $.ajaxSetup({
        url: "/setribbon",
        global: false,
        type: "POST",
        data: {
    		'pointURL': $('#pointArea').data('pointurl'),
    		'ribbon':newRibbonValue
    		},
        success: function(obj){
            if (obj.result == true) {
              updateRibbon(newRibbonValue, obj.ribbonTotal);
            } else {
              alert('An error happened and your award may not have counted. Try after a page refresh?');
            }
        }
    });
    $.ajax();
}

function updateRibbon(newRibbonValue, ribbonTotal) {
    $("#blueRibbon").data("ribbonvalue", newRibbonValue);
    if (newRibbonValue) {
        $("#blueRibbon").removeClass("notAwarded");   
        $("#blueRibbon").removeClass("hover");  
        $("#blueRibbon").addClass("awarded");                     
    } else {
        $("#blueRibbon").removeClass("hover");                
        $("#blueRibbon").removeClass("awarded");
        $("#blueRibbon").addClass("notAwarded");        
    }
    $("#ribbonTotal").text(ribbonTotal);
}

function deletePoint(urlToDelete) {
    $.ajaxSetup({
        url: "/deletePoint",
        global: false,
        type: "POST",
        data: {
            'urlToDelete': urlToDelete
            },
        success: function(obj){
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

function populateEditFields() {
    var ed = tinyMCE.get('editor_pointDialog');

    $('div.modal-header h3', $('#pointDialog')).text("Edit Point");

    $('#title_pointDialog').val($('#mainPointTitle').text());
    setCharNumText($('#title_pointDialog')[0]);
    if (ed) {
        ed.setContent($('#pointSummary .mainPointContent').html() );
        /* ATPT IN PROGRESS: this code will be used to create working placeholder text in the additional text area */
        // hide placeholder-label
        if(ed.getContent() != '') {
            $('label[for="mceEditor"]').hide();
        } 
    }
    
    $('#author_pointDialog').val($('#mainPointImageArea .mainPointImageAuthor').text());
    $('#description_pointDialog').val($('#mainPointImageArea .mainPointImageCaption').text());
    var url = $('#pointSummary div.mainPointImageURL').text();
    $('#link_pointDialog').val(url);

    var sourcesCount = 0;
    $('[name=mainPointSource] a').each(function(i, obj) {    
      var sourcekey = $(obj).data('sourcekey');
      addSourceHTML($(obj).attr('href'), $(obj).text(), sourcekey);
      sourcesCount = sourcesCount + 1;
    });
    /*
    if (sourcesCount > 0 ) {
       //$("#sourcesPanelTitle .panel-heading").text(sourcesCount + (sourcesCount == 1?" Source":" Source"));
       $("#sourcesPanelTitle .panel-heading").text("Add Sources");     
    } else {
       $("#sourcesPanelTitle .panel-heading").text("0 Sources (add some to improve this)");
    }
    */

    if(url !== '') {
        if(url.match("https?://")) {
            $('.filepicker-placeholder').attr('src', url);
        } else {
            $('.filepicker-placeholder').attr('src', '//d38pzqn4b9ae2a.cloudfront.net/SummaryMedium-'+encodeURIComponent(url));
        }
    }
}

function selectPoint(supportingPointURL, currentPointURL, linkType){
  	$.ajaxSetup({
		url: "/linkPoint",
		global: false,
		type: "POST",
	 	data: {
			'supportingPointURL': supportingPointURL,
			'parentPointURL': currentPointURL,
			'linkType': linkType
			},
		success: function(obj){
		  if (obj.result == true) {
              pointListAppend(linkType, obj.newLinkPoint, obj.numLinkPoints);
			  updateVersionHeader(obj.authorURL, obj.author, obj.dateEdited);		  
		  } else {
            if (obj.error) {
                showAlert('<strong>Oops!</strong> There was an error: ' + obj.error);
            } else {
                showAlert('<strong>Oops!</strong> There was an error: ');
            }
		  }
          $("#linkedPointSearchDialog").modal('hide');
		},
		error: function(xhr, textStatus, error){
            showAlert('The server returned an error. You may try again.');
            $("#linkedPointSearchDialog").modal('hide');
        }
	});
	$.ajax();
}

function setPointListHeader(linkType) {
	numLinkPoints = $("#" + linkType + "_nonzeroPoints").find('.pointCard').length;
    if (numLinkPoints == 0) {
        header = "Zero " + linkType.capitalize() + " Points";
    } else {
        header = numLinkPoints + " " +  linkType.capitalize() + (numLinkPoints == 1 ? " Point":" Points");
    }
    $("#"+linkType+"_numberOfPoints").text( header );
}

function pointListAppend(linkType, pointHTML, numLinkPoints) {

    var newPointCard = $(pointHTML).appendTo("#" + linkType + "_nonzeroPoints");    
    // no longer being used:
    //setPointListHeader(linkType);	
    makePointsCardsClickable();	 
    makeRelevanceControlsClickable();
    $('[name=showRelevance]').off('.ys').on('click.ys', showRelevance);
    $('[name^=relevanceRadio]').off('.ys').on('click.ys', sendRelevanceVote);        
    
    if ($("[id^=" + linkType +"Point_]").length == 0 ) {
      $("#" + linkType + "_zeroPoints").hide();
      $("#" + linkType + "_nonzeroPointsFooter").removeClass("hide");
      $("#" + linkType + "_nonzeroPoints").show();
    }
    	
    var position = newPointCard.offset();
    $("html, body").animate({ scrollTop: position.top - newPointCard.height() - 60}, "slow");
    
}


function tryAddSupporting(linkType, ajaxData, retries) {
	$.ajaxSetup({
		url: "/addSupportingPoint",
		global: false,
		type: "POST",
		data: ajaxData,
		success: function(obj){
			if (obj.result == true) {
                pointListAppend(linkType, obj.newLinkPoint, obj.numLinkPoints);
  			  	updateVersionHeader(obj.authorURL, obj.author, obj.dateEdited);
  			  	if (obj.parentNewScore != null) {
  			  	    updatePointScore(obj.parentNewScore, $('#pointScoreSpan'))
                }
                stopSpinner();                
    		    $("#pointDialog").modal('hide');
                enableDialogButtons('#submit_pointDialog');
			} else {
                errorMessage = obj.errMessage || null;
                console.log(obj);
				if (errorMessage) {
                    clearEditDialogAlert();
                    // really this needs to pass back a different code from the back end. I sin again.
                    if (errorMessage.indexOf('point because someone else was editing this point at the same time.  Please try again.') > -1) {
                        if (retries < 5) {
                            var newRetries = retries + 1;
                            errorMessage = 'Other users are editing the point, your point is taking a bit longer to be added.  Please wait. (Retry ' + newRetries.toString() + ').';
                            
                            console.log('Retry error message was: ' + errorMessage);
        		    		editDialogAlert(errorMessage);                            
                            setTimeout(function() {tryAddSupporting(linkType, ajaxData, newRetries);}, 900);
                        } else {
                            errorMessage = 'Too many attempts, please wait and hit publish again.';
        		    		editDialogAlert(errorMessage);
                            stopSpinner();
                            enableDialogButtons('#submit_pointDialog');
                        }
                    }
		    	} else {
                    console.log('EM' + errorMessage);
                    console.log('OERRR' + obj.errMessage);
		    		editDialogAlert("There was an error");
                    stopSpinner();
                    enableDialogButtons('#submit_pointDialog');
		    	}
			}
		},
		fail: function(xhr, textStatus, errorThrown){
            editDialogAlert('The server returned an error: ' + errorThrown + ' You may try again.');
            stopSpinner();
            enableDialogButtons('#submit_pointDialog');
        }
	});
	$.ajax();
}

function addPoint(linkType){
    unlinkVisible = !$("[id^=unlink_" + linkType + "]").hasClass("ui-helper-hidden");
    if (unlinkVisible) toggleUnlink(linkType);

    if ($('#title_pointDialog').val().length > MAX_TITLE_CHARS) {
        editDialogAlert('Please do not exceed 200 characters for the title.');
        return;
    }
    
    if ($('#title_pointDialog').val().length == "") {
        editDialogAlert('To create a point you must enter something for the title!');      
        return;
    }
    
    if (!addCurrentSource()) { return; }  
    
	var ed = tinyMCE.get('editor_pointDialog');
    var text = tinyMCE.activeEditor.getBody().textContent;  
    //$('#submit_pointDialog').off('click');
    //$('#submit_pointDialog').hide();
    //$('#submit_pointDialog').after("<img id=\"spinnerImage\" src=\"/static/img/ajax-loader.gif\"/>");
    disableDialogButtons('#submit_pointDialog');
    
    $('#submit_pointDialog').text("Publish to Library...");
    $('#submit_pointDialog').after("<img id=\"spinnerImage\" class=\"spinnerPointSubmitButtonPosition\" src=\"/static/img/ajax-loader.gif\"/>");     
    
    var ajaxData =  {
		'content': ed.getContent(),
        'plainText': text.substring(0,500),
		'title': $('#title_pointDialog').val(),
		'linkType':linkType,
		'pointUrl': $('#pointArea').data('pointurl'),
		'imageURL':$('#link_pointDialog').val(),
        'imageAuthor':$('#author_pointDialog').val(),
        'imageDescription': $('#description_pointDialog').val(),
        'sourcesURLs': JSON.stringify(getNewSourcesURLs()),
        'sourcesNames': JSON.stringify(getNewSourcesNames())
	};
    
    tryAddSupporting(linkType, ajaxData, 0);
	
}

function linkPointControlsInitialState() {
    $( ".whybutton" ).button();
    $( ".unlinkbutton" ).button();
    $( ".unlinkbutton" ).addClass("ui-helper-hidden");
    $( ".ui-helper-hidden" ).hide();
}



function setUpMenuAreas() {
    // Dropdown add of the recently viewed points
    $("[name^=selectPoint_menu_]").off('.ys').on('click.ys', function(e){
        var theLink = $(this);
        
        var linkPointURL = theLink.data('pointurl');
        var parentPointURL = $('#pointArea').data('pointurl');
        var linkType =  theLink.data('linktype');
        // _gaq.push(['_trackEvent', 'Link Manipulation',
        //     'Added ' + linkType + ' from recently viewed',
        //     linkPointURL + ' to ' + parentPointURL]);
        ga('send', 'event', 'Link Manipulation',
            'Added ' + linkType + ' from recently viewed',
            linkPointURL + ' to ' + parentPointURL);
        selectPoint(linkPointURL, parentPointURL, linkType);
        $("[name^=selectPoint_menu_]").filter("*[data-pointurl=\""+ linkPointURL + "\"]").remove();
    });

    // Edit the current point
    $( "#editPoint" ).off('.ys').on('click.ys', function() {
        populateEditFields();
        showPointDialog("edit", "Edit Point");        
    });
    
    $( "#addImage" ).off('.ys').on('click.ys', function() {
        populateEditFields();
        showPointDialog("edit", "Edit Point");
    });
    
    $( "#changeImage" ).off('.ys').on('click.ys', function() {
        populateEditFields();
        showPointDialog("edit", "Edit Point");
        
    });

    // Create a new linked point
    $( "[name=createLinked]" ).off('.ys').on('click.ys', function() {
        var linkType = $(this).data('linktype');
        $("#submit_pointDialog").data("linktype", linkType);
        var dialogName = "Create " + linkType.capitalize() + " Point";
        showPointDialog("createLinked", dialogName);        
    });
    
    // Show the search dialog
    $( "[name$=_searchForPoint]" ).off('.ys').on('click.ys', function(e){
        linktype = $(this).data('linktype');
        $("#selectLinkedPointSearch").data("linkType", linktype);
        $("#linkedPointSearchDialog .modal-header h3").text('Search for ' + linktype + ' points for:');  
        $("#linkedPointSearchDialog .modal-header h1").text($('#mainPointTitle').text());                      
        $("#linkedPointSearchDialog").modal('show');
        $('body, html').animate({ scrollTop: 0}, 500);        
    });
    
  
    // These elements are admin only, but jquery degrades gracefully, so not checking for their presence
    $('#changeEditorsPickTrigger').off('.ys').on('click.ys', function() {
        title = $('#mainPointTitle').text();
        $("#changeEditorsPick .modal-header h4").text(title);
        $("#changeEditorsPick").modal('show');
    });

    $('#submitChangeEditorsPick').off('.ys').on('click.ys', changeEditorsPick);

    // These elements are admin only, but jquery degrades gracefully, so not checking for their presence
    $('#changeLowQualityAdminTrigger').off('.ys').on('click.ys', function() {
        title = $('#mainPointTitle').text();
        $("#changeLowQualityAdmin .modal-header h4").text(title);
        $("#changeLowQualityAdmin").modal('show');
    });
    
    $('#submitChangeLowQualityAdmin').off('.ys').on('click.ys', changeLowQualityAdmin);
    
    $('#makeFeaturedPick').off('.ys').on('click.ys', makeFeaturedPick);   
    $('#refreshTopStatus').off('.ys').on('click.ys', refreshTopStatus);
}


function insertComment(commentObj) {
    html = "<div class=\"row-fluid cmmnt level" + commentObj.level + "\">" +
      "<div class=\"cmmnt-content span11\">" + commentObj.text + "<a href=\"/user/"+  commentObj.userURL +
      "\" class=\"userlink\">" + commentObj.userName + "</a> - <span class=\"pubdate\">"  + commentObj.date + 
      "</span> </div> <div class=\"span1\">" +
          "<a name=\"commentReply\" data-parentkey="+ commentObj.myUrlSafe + ">Reply</a></div></li>"
          
    if (!commentObj.parentUrlsafe || commentObj.parentUrlsafe == '') {
        $('#comments').prepend(html);        
    } else {
        linkToInsertBelow = $("a[data-parentkey=\"" + commentObj.parentUrlsafe + "\"]");
        linkToInsertBelow.parent().parent().after(html);
    }
    
    $("[name=commentReply]").unbind("click", showReplyComment);    
    $("[name=commentReply]").on("click", showReplyComment);
    setCommentCount(null);
}

function showReplyComment(event) {
    $('#addComment').removeClass('hide');
    tinyMCE.execCommand('mceRemoveControl', false, 'commentText');
    $("#addComment").insertAfter($(event.target).parent().parent());
    initTinyMCE();
    $("#addComment").data('parentkey', $(event.target).data('parentkey'));
    $('body, html').animate({ scrollTop: $("#addComment table").offset().top - 100 }, 500);
    $('#showAddComment').parent().removeClass('hide');    
}

function showRelevance(event) {
    relArea = $(this).next();
    if (relArea.hasClass('hide')) {
        $('.relevanceVote').addClass('hide'); // hide any other open relevance area
        relArea.removeClass('hide');
    } else {
        relArea.addClass('hide');
    }
}

function sendRelevanceVote(event) {
    var selectedRadioButton = $(this)
    if ($(this).hasClass('styledRadio')) {
        // we got called on the screwdefaultbuttons button
        selectedRadioButton = $(this).children(":first");
    }
    var relBase = selectedRadioButton.closest('[name=areaRelevanceRadio]');
    var radioButtons = $("[type=radio]", relBase);
    
    radioButtons.screwDefaultButtons("disable");
    $('.styledRadio').off('.ys');        
    voteValue = selectedRadioButton.val();	
    linkType = relBase.data('linktype');
    parentRootURL = $('#pointArea').data('rootus');
    childRootURL = relBase.data('childurlsafe');
    
    //_gaq.push(['_trackEvent', 'Vote', 'Relevance of ' + linkType , voteValue]);
    ga('send', 'event', 'Vote', 'Relevance of ' + linkType, voteValue);
                        
    $.ajaxSetup({
		url: "/relVote",
		global: false,
		type: "POST",
		data: {
            'parentRootURLsafe': parentRootURL,
            'childRootURLsafe': childRootURL,
            'linkType': linkType,
            'vote': voteValue,
		},
		success: function(obj){
			if (obj.result == true) {
                
                // switching from .text() to .html() in order to insert the pencil -JF
                //selectedRadioButton.closest('[name="areaRelevanceRadio"]').prev().text(
                //    'Relevance ' + obj.newRelevance); 
                selectedRadioButton.closest('[name="areaRelevanceRadio"]').prev().html(
                    'Relevance ' + obj.newRelevance + '<img class="relevanceEditIcon" src="/static/img/pencil_icon_blue.png"/>'); 
                selectedRadioButton
                    .closest('[name="areaRelevanceRadio"]')
                    .children('[name=relevanceTextLine]')
                    .text(
                        obj.newVoteCount + " User" + ( obj.newVoteCount > 1 ? "s":"") +
                        " Voting.   Curent Average: " + obj.newRelevance);
  			  	if (obj.parentNewScore != null) {
  			  	    updatePointScore(obj.parentNewScore, $('#pointScoreSpan'))
                }
            } else {
			    showAlertAfter('Not able to save vote. Try to refresh the page.', 
                    selectedRadioButton.closest('[name=areaRelevanceRadio]'));
                
            }
            radioButtons.screwDefaultButtons("enable");
            $('.styledRadio').off('.ys').on('click.ys', sendRelevanceVote);
            relBase.addClass('hide');
		},
		error: function(xhr, textStatus, error){
            showAlertAfter('The server returned an error. You may try again.', "#addComment");
            stopSpinnerOnButton('#saveCommentSubmit', saveComment);
            radioButtons.screwDefaultButtons("enable");
            $('.styledRadio').off('.ys').on('click.ys', sendRelevanceVote);                	                                                
        }
	});
	$.ajax();
}

function saveComment(event) {
    var ed = tinyMCE.get('commentText');
    commentText = ed.getContent();    
    if (commentText.trim() == '') return;
    
    pointURL = $('#pointArea').data('pointurl');
    ga('send', 'event', 'Comment', 'Comment', pointURL);
    
    startSpinnerOnButton('#saveCommentSubmit');    
    $.ajaxSetup({
		url: "/saveComment",
		global: false,
		type: "POST",
		data: {
		    'commentText': ed.getContent(),
        	'p':$('#rootUrlSafe').val(),
        	'parentKey': $('#addComment').data('parentkey')
		},
		success: function(obj){
			if (obj.result == true) {
                insertComment(obj);
                ed.setContent('');                                              
                stopSpinnerOnButton('#saveCommentSubmit', saveComment);
                $('#addComment').addClass('hide');  
                $('#addComment').data('parentkey', '');
			} else {
			    showAlertAfter(obj.error ? obj.error: "There was an error", "#addComment");
                stopSpinnerOnButton('#saveCommentSubmit', saveComment);
			}
		},
		error: function(xhr, textStatus, error){
            showAlertAfter('The server returned an error. You may try again.', "#addComment");
            stopSpinnerOnButton('#saveCommentSubmit', saveComment);
        }
	});
	$.ajax();
    
}

function archiveComments(event) {
    var commentKey = $(event.target).data('commentkey');
    var pointKey = $('#rootUrlSafe').val();
    var commentRow = event.target.parentElement.parentElement;
    startSpinnerOnButton(event.target);    
    $.ajaxSetup({
		url: "/archiveComments",
		global: false,
		type: "POST",
		data: {
		    'rootKey': pointKey,
        	'parentKey': commentKey
		},
		success: function(obj){
			if (obj.result == true) {                
                var currentElement = $(commentRow);
                for (var i=0;i<obj.numArchived;i++)
                { 
                    currentElement.hide();
                    currentElement = currentElement.next();
                }
                showAlertTypeAfter('This comment thread (' + obj.numArchived + ' comments) has been archived.', 
                    commentRow, "alert-success")
                stopSpinnerOnButton(event.target, saveComment);                
			} else {
			    showAlertAfter(obj.error ? obj.error: "There was an error", commentRow);
                stopSpinnerOnButton(event.target, saveComment);
			}
		},
		error: function(xhr, textStatus, error){
            showAlertAfter('The server returned an error. You may try again.',commentRow);
            stopSpinnerOnButton(event.target, saveComment);
        }
	});
	$.ajax();    
}

function showArchivedComments(event) {
    var pointKey = $('#rootUrlSafe').val();
    startSpinnerOnButton(event.target);    
    $.ajaxSetup({
		url: "/getArchivedComments",
		global: false,
		type: "POST",
		data: {
		    'rootKey': pointKey,
		},
		success: function(obj){
			if (obj.result == true) {                
                $('#archivedComments').html(obj.html);
			} else {
			    showAlertAfter(obj.error ? obj.error: "There was an error", event.target);
			}
            stopSpinnerOnButton(event.target, event.target);
		},
		error: function(xhr, textStatus, error){
            showAlertAfter('The server returned an error. You may try again.',event.target);
            stopSpinnerOnButton(event.target, event.target);
        }
	});
	$.ajax();    
}





function changeEditorsPick() {
    pick = $('#editorsPick').get(0).checked;
    pickSort = $("#editorsPickSort").val();
    if (pick && !isNormalInteger(pickSort)) {
        showAlertAfter('Editors Pick must have a positive whole number for Editors Pick Sort', '#changeEditorsPick [name="alertArea"]');
    } else {
        startSpinnerOnButton('#submitChangeEditorsPick');        
        $.ajaxSetup({
    		url: "/changeEditorsPick",
    		global: false,
    		type: "POST",
    		data: {
    			'urlToEdit': $('#pointArea').data('pointurl'),
    			'editorsPick': pick,
    			'editorsPickSort': pickSort
    		},
    		success: function(obj) {
    			if (obj.result == true) {
    		        // set the values in the main point page
        		    if (pick) {
        		        $('#changeEditorsPickTrigger').text('Editors Pick: True - ' + pickSort);  		        		        
        		    } else {
        		        $('#changeEditorsPickTrigger').text('Editors Pick: False');         		        
        		    }
        		    stopSpinnerOnButton('#submitChangeEditorsPick', changeEditorsPick);
        		    $('#changeEditorsPick').modal('hide');
        		    showSuccessAlert('Editors Picks updated.')    		    
        		} else {
        		    showAlertAfter('Server error: ' + obj.error + '. You may try again.', '#changeEditorsPick [name="alertArea"]');                    
        		    stopSpinnerOnButton('#submitChangeEditorsPick', changeEditorsPick);          		    
        		}        		          
    		},    		
    	});
    	$.ajax();
    }
}

function changeLowQualityAdmin() {
    pick = $('#lowQualityAdmin').get(0).checked;
    {
        startSpinnerOnButton('#submitChangeLowQualityAdmin');
        $.ajaxSetup({
    		url: "/changeLowQualityAdmin",
    		global: false,
    		type: "POST",
    		data: {
    			'urlToEdit': $('#pointArea').data('pointurl'),
    			'lowQuality': pick
    		},
    		success: function(obj) {
    			if (obj.result == true) {
    		        // set the values in the main point page
        		    if (pick) {
        		        $('#changeLowQualityAdminTrigger').text('Low Quality: True');
        		    } else {
        		        $('#changeLowQualityAdminTrigger').text('Low Quality: False');
        		    }
        		    stopSpinnerOnButton('#submitChangeLowQualityAdmin', changeLowQualityAdmin);
        		    $('#changeLowQualityAdmin').modal('hide');
        		    showSuccessAlert('Low Quality updated.')
        		} else {
        		    showAlertAfter('Server error: ' + obj.error + '. You may try again.', '#changeLowQualityAdmin [name="alertArea"]');
        		    stopSpinnerOnButton('#submitChangeLowQualityAdmin', changeLowQualityAdmin);
        		}
    		},
    	});
    	$.ajax();
    }
}

function viewPointHistory() {
    $('#viewPointHistory').parent().after("<img id=\"historyAreaLoadingSpinner\" src=\"/static/img/ajax-loader.gif\"/>");
    
	$('#leftColumn .tabbedArea').hide();
	$('#leftColumn #historyArea').show();
	$.ajax({
		url: '/pointHistory',
		type: 'GET',
		data: { 'pointUrl': $('#pointArea').data('pointurl') },
		success: function(obj) {
			$('#historyAreaLoadingSpinner').remove();
			$('#historyArea').html(obj.historyHTML);
			makePointsCardsClickable();	
		    $('#viewSupportingPoints').off('.ys').on('click.ys', function() {
				$('#leftColumn #supportingPointsArea').show();
				$('#leftColumn #historyArea').hide();			
		    });    
		},
		error: function(data) {
			$('#historyArea').empty();
			showAlert('<strong>Oops!</strong> There was a problem loading the point history.  Please try again later.');
		},
	});
}

function makeRelevanceControlsClickable() {
    $('[name=showRelevance]').off('.ys').on('click.ys', showRelevance);
    $('input:radio').screwDefaultButtons({
            image: 'url("/static/img/screwdefault_radio_design_roSpinner.gif")',
            width: 45,
            height: 45
    });
    $('[name^="relevanceRadio"]').off('.ys').on('click.ys', sendRelevanceVote);                	
    $('.styledRadio').off('.ys').on('click.ys', sendRelevanceVote);
}

function sharePointOnTwitter() {
    var url = $('#pointArea').data('pointurl');
    var pointTitle = $('#mainPointTitle').text();
    var len = pointTitle.length;
    var text = "";
    if (len > 115) {
        text = pointTitle.substring(0,114) + "..." + "https://www.whysaurus.com/point/" + url;
    } else {
        text = pointTitle + " https://www.whysaurus.com/point/" + url;        
    }
    var webUrl = "http://twitter.com/intent/tweet?text="+encodeURIComponent(text);   
    window.open(webUrl,'_blank');        
}

function postOnFacebook() {
    var url = $('#pointArea').data('pointurl');
    var pointTitle = $('#mainPointTitle').text();
    var dialogParams = {
        app_id: 144595249045851,
        method: 'feed',
        link: "https://www.whysaurus.com/point/" + url,
        name: pointTitle,        
        description: 'Debating on whysaurus: ' + pointTitle + ' \n Do you agree? Disagree? Got something to add to the debate?'
    };
    var imageUrl = $(".pointDisplay").attr('src') || null;

    if (!imageUrl) {
        // if there is no image in the page, pass the logo
        imageUrl = window.location.protocol + "//" + window.location.host + "/static/img/whysaurus_logo.png";
        dialogParams['picture'] = imageUrl;                
    } else {
        imageUrl = imageUrl.slice(2);
    }
    
    FB.ui(dialogParams, function(response){});
}

// should this get replaced by adding fields to the database?
function setPointCreator() { 
    pointURL = $('#pointArea').data('pointurl');
	$.ajax({
		url: '/getPointCreator',
		type: 'GET',
		data: { 'pointURL': pointURL },
    	success: function(obj) {
    			if (obj.result == true) {                    
                    $('#pointCreator').html('Begun by: <a target="_blank" href="../user/'+ obj.creatorURL +'">'+ obj.creatorName +'</a> ');

                    /* Code for listing number of contributors
                    if (obj.numAuthors > 1) { 
                        ContributorPluralCheck = 'Contributors' } 
                    else { 
                        ContributorPluralCheck = 'Contributor' }                        
                    $('#pointCreator').html('Begun by: <a target="_blank" href="../user/'+ obj.creatorURL +'">'+ obj.creatorName +'</a><br>'+ obj.numAuthors +' '+ ContributorPluralCheck +',  ');
                    */
                    //showSuccessAlert(obj.creatorURL + ' ' + obj.creatorName);   // echo for debugging                    
        		} else {
        		    showErrorAlert('Error setting creator');                    
        		}        		          
    	},         
	});  
}

function activateCommentHint() {    
    $('#commentHintLink').click(function () {
         $($('#commentHint'), this).toggle();
    });   
}

function activatePointArea() {    
    if (!loggedIn) {        
        make_this_show_login_dlg($( "[id$=addPointWhenNonZero]" ));
        make_this_show_login_dlg($( "[id$=addPointWhenZero]" ));
        make_this_show_login_dlg($( "#editPoint" ));
        make_this_show_login_dlg($( "#changeImage" ));
        make_this_show_login_dlg($( "#addImage" ));        
        make_this_show_login_dlg($( "#upVote" ));
        make_this_show_login_dlg($( "#downVote" ));
        make_this_show_login_dlg($( "#viewPointHistory" ));
        make_this_show_login_dlg($( "#showAddComment" ));
        make_this_show_login_dlg($( "[name=commentReply]" ));    
        make_this_show_login_dlg($( "[name=showRelevance]" ));     
    } else {


        $( "#upVote" ).click(function() {upVote();});
        $( "#downVote" ).click(function() {	downVote();	});
        $( "#blueRibbon" ).click(function() {changeRibbon();});        

        setUpMenuAreas();
        
        //setPointCreator();
        
        $('#showAddComment').click(function() {
            tinyMCE.execCommand('mceRemoveControl', false, 'commentText');
            $("#addComment").insertAfter($(event.target).parent());            
            initTinyMCE();            
            $('#addComment').removeClass('hide');
            $('#showAddComment').parent().addClass('hide');
            $('#addComment').data('parentkey', '');
            $('body, html').animate({ scrollTop: $("#addComment table").offset().top - 100 }, 500);        
        });
        
        $('#saveCommentSubmit').off('.ys').on('click.ys', saveComment);    
        $( "#deletePoint" ).button();
	    $('#viewPointHistory').off('.ys').on('click.ys',viewPointHistory);	
        
        $('[name=commentReply]').click(showReplyComment);
        $('[name=commentArchive]').click(archiveComments);
        $('#commentViewArchived').click(showArchivedComments);

        
        makeRelevanceControlsClickable();      	        
        // $('[name^=relevanceRadio]:checked').screwDefaultButtons('check');
    }    
	
    activateCommentHint();
    
	// if low relevance SPs exist, show the toggle
	if ($("#supporting_nonzeroPoints div[name=showRelevance].belowThreshold").length > 0) {
		$('[id$=supporting_showBelowArea]').show();
	}
		
	// if low relevance CPs exist, show the toggle
	if ($("#counter_nonzeroPoints div[name=showRelevance].belowThreshold").length > 0) {
		$('[id$=counter_showBelowArea]').show();
	}
	
	// functions to operate toggle button
    $('#supporting_showBelowThreshold').click( function() {
        $("#supporting_nonzeroPoints .belowThreshold").toggle();
    });    
    $('#counter_showBelowThreshold').click( function() {
        $("#counter_nonzeroPoints .belowThreshold").toggle();
    });    
           
    $('#tweet').click(sharePointOnTwitter);
    $('#postOnFacebook').click(postOnFacebook);
    
    makePointsCardsClickable();	    

    // Menus going up the tree
    $('[name="pointNavMenu"]').click(function(ev) {
        if (ev.metaKey || ev.ctrlKey) {
            return;
        } else {
            // Trim off the "/point/" before dynamic load
            loadPoint($(this).attr('href').substring(7), true);
            ev.preventDefault();
        }
    });

    // Hide the history area and show the supporting points area
    $('#leftColumn .tabbedArea').hide(); $('#supportingPointsArea').show();

}

function makeFeaturedPick() {
     $.ajaxSetup({
    		url: "/makeFeatured",
    		global: false,
    		type: "POST",
    		data: {
    			'urlToEdit': $('#pointArea').data('pointurl')
    		},
    		success: function(obj) {
    			if (obj.result == true) {
    		        showSuccessAlert('This is now the featured point.')
        		} else {
        		    showErrorAlert('Server error: ' + obj.error + '. You may try again.', '#changeEditorsPick [name="alertArea"]');                    
        		}        		          
    		},    		
    	});
    	$.ajax();
}

function refreshTopStatus() {   
         $.ajaxSetup({
    		url: "/refreshTopStatus",
    		global: false,
    		type: "POST",
    		data: {
    			'urlToEdit': $('#pointArea').data('pointurl')
    		},
    		success: function(obj) {
    			if (obj.result == true) {
    		        showSuccessAlert('Top Status Refreshed.')
        		} else {
        		    showErrorAlert('Server error: ' + obj.error + '. You may try again.', '#changeEditorsPick [name="alertArea"]');                    
        		}        		          
    		},    		
    	});
    	$.ajax();
    //showSuccessAlert('here.')  
}



$(document).ready(function() {
    activatePointArea();
});

//@ sourceURL=/static/js/point.js
