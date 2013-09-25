var CONST_EDITOR_DEFAULT_TEXT = 'Add the description here...';
var MAX_TITLE_CHARS = 140;

function showAlert(alertHTML) {
    $('#mainContainer').prepend($('<div class="alert"><button type="button" class="close" data-dismiss="alert">&times;</button>' + alertHTML + '</div>'));
}

function showAlertAfter(alertText, elementSelector) {
        $(elementSelector).after($('<div class="alert"><button type="button" class="close" data-dismiss="alert">&times;</button>' + alertText + '</div>'));
}

function showErrorAlert(alertHTML) {
    $('#mainContainer').prepend($('<div class="alert alert-error"><button type="button" class="close" data-dismiss="alert">&times;</button>' + alertHTML + '</div>'));
}

function showSuccessAlert(alertText) {
    $('#mainContainer').prepend($('<div class="alert alert-success"><button type="button" class="close" data-dismiss="alert">&times;</button>' + alertText + '</div>'));
}

function validateURL(textval) {
     return textval.match(/^(ht|f)tps?:\/\/[a-z0-9-\.]+\.[a-z]{2,4}\/?([^\s<>\#%"\,\{\}\\|\\\^\[\]`]+)?$/);
}

function validateEmail(textval) {
     return textval.match(/^[A-Z0-9._%-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$/i);
}

function validatePassword(textval) {
     return textval.match(/[A-Za-z]/) && textval.match(/[0-9]/);
}
   
function startSpinnerOnButton(buttonID) {
   $(buttonID).off('click');
   $(buttonID).hide();
   $(buttonID).after("<img id=\"spinnerImage\" src=\"/static/img/ajax-loader.gif\"/>");
}

function stopSpinnerOnButton(buttonID, clickHandler) {
   $("#spinnerImage").remove();
   $(buttonID).click( clickHandler );        
   $(buttonID).show();
}
   
function post_to_url(path, params, method) {
  method = method || "post"; // Set method to post by default, if not specified.

  // The rest of this code assumes you are not using a library.
  // It can be made less wordy if you use one.
  var form = document.createElement("form");
  form.setAttribute("method", method);
  form.setAttribute("action", path);

  for (var key in params) {
    if (params.hasOwnProperty(key)) {
      var hiddenField = document.createElement("input");
      hiddenField.setAttribute("type", "hidden");
      hiddenField.setAttribute("name", key);
      hiddenField.setAttribute("value", params[key]);
      form.appendChild(hiddenField);
    }
  }

  document.body.appendChild(form);
  form.submit();
}

String.prototype.capitalize = function() {
    return this.replace(/(?:^|\s)\S/g, function(a) { return a.toUpperCase(); });
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

function getCaretPosition (oField) {

    // Initialize
    var iCaretPos = 0;

    // IE Support
    if (document.selection) {

      // Set focus on the element
      oField.focus ();

      // To get cursor position, get empty selection range
      var oSel = document.selection.createRange ();

      // Move selection start to 0 position
      oSel.moveStart ('character', -oField.value.length);

      // The caret position is selection length
      iCaretPos = oSel.text.length;
    }

    // Firefox support
    else if (oField.selectionStart || oField.selectionStart == '0')
      iCaretPos = oField.selectionStart;

    // Return results
    return (iCaretPos);
}


function positionEditDialog() {
  dialogHeight = $(".pointDialog").height();
  $("[id$='_ifr']").height(dialogHeight - 550);
}

function getNewSourcesURLs() {
    var links  = $('.sourceLink');
    var urls = [];    
    for(var i = 0; i < links.length; i++){
        var sourcekey = $(links[i]).parent().data('sourcekey');
        if (!sourcekey) {
            urls.push($(links[i]).attr('href'));          
        }
    }
    return urls;
}

function getNewSourcesNames() {
    var links  = $('.sourceLink');
    var sources = [];    
    for(var i = 0; i < links.length; i++){
        var sourcekey = $(links[i]).parent().data('sourcekey');
        if (!sourcekey) { 
            sources.push($(links[i]).text());
        }
    } 
    return sources;
}

function newPoint() {
  if ($('#title_pointDialog').val().length > MAX_TITLE_CHARS) {
      editDialogAlert('Please do not exceed 140 characters for the title.');
      return;
  }
  if ($('#title_pointDialog').val().length == "") {
      editDialogAlert('To create a point you must enter something for the title!');      
      return;
  }
  
  var ed = tinyMCE.get('editor_pointDialog');
  var text = tinyMCE.activeEditor.getBody().textContent;
  $("#submit_pointDialog").off('click');
  $("#submit_pointDialog").hide();
  $("#submit_pointDialog").after("<img id=\"spinnerImage\" src=\"/static/img/ajax-loader.gif\"/>");
  var u = getNewSourcesURLs();
  var n = getNewSourcesNames();
  $.ajaxSetup({
    url: "/newPoint",
    global: false,
    type: "POST",
    data: {
      'content': ed.getContent(),
      'plainText': text.substring(0, 250),
      'title': $('#title_pointDialog').val(),
      'imageURL': $('#link_pointDialog').val(),
      'imageAuthor': $('#author_pointDialog').val(),
      'imageDescription': $('#description_pointDialog').val(),
      'sourcesURLs': JSON.stringify(u),
      'sourcesNames': JSON.stringify(n)
    },
    success: function(data) {
      obj = JSON.parse(data);
      if (obj.result === true) {
        var params = [];
        params["rootKey"] = obj.rootKey;
        post_to_url("/point/" +  obj.pointURL, params);
      } else {
        editDialogAlert(obj.result);
    	stopSpinner();
      }
    },
    error: function(xhr, textStatus, error){
        editDialogAlert('The server returned an error: ' + xhr + '. You may try again.');
    	stopSpinner();
    }
  });
  $.ajax();
}

function openNewPointDialog() {
  document.getElementById("textEdit_tbl").style.width = '100%';
  document.getElementById("textEdit_ifr").style.width = '100%';
  document.getElementById("textEdit_tbl").style.height = '100%';
  document.getElementById("textEdit_ifr").style.height = '100%';
  var dialogButtons = {};
  dialogButtons["Create Point"] =

  dialogButtons["Cancel"] = function() {

    $(this).dialog("close");
  };

  $("#dialogForm").dialog({
    title: "New Point",
    buttons: dialogButtons
  });
  $("#dialogForm").dialog("open");
}

function openLoginDialog() {
  var dialogButtons = {};
  dialogButtons["Cancel"] = function() {
    $(this).dialog("close");
  };
  $("#loginDialog").dialog({
    title: "Sign In",
    buttons: dialogButtons
  });
  $("#loginDialog").dialog("open");
}

function showCreatePoint() {
  $("#CreatePoint").css('visibility', 'visible');
}

function clearDefaultContent(ed) {
  // replace the default content on focus if the same as original placeholder
  currentContent = ed.getContent();
  slen = currentContent.length;
  currentContent = currentContent.substring(3, slen - 4);
  var is_default = (currentContent == CONST_EDITOR_DEFAULT_TEXT);

  if (is_default) {
    ed.setContent('');
  }
}

function setCharNumText(titleField) {
    var numLeft = MAX_TITLE_CHARS ;
    if (titleField && titleField.value) {
        numLeft = MAX_TITLE_CHARS - titleField.value.length;
    }

    if (numLeft < 0) {
        $("#" + titleField.id + "_charNum").text(numLeft*-1 + " characters over limit");
        $("#" + titleField.id + "_charNum").addClass("redScore");
    } else {
        $("#" + titleField.id + "_charNum").text(numLeft + " characters left");
        $("#" + titleField.id + "_charNum").removeClass("redScore");
    }
}

function dialogAlert(dialogID, alertHTML) {
    $(dialogID + ' #alertArea').prepend($('<div class="alert"><button type="button" class="close" data-dismiss="alert">&times;</button>' + alertHTML + '</div>'));  
}

function editDialogAlert(alertHTML) {
    dialogAlert('#pointDialog', alertHTML);
}

function stopSpinner() {
    $("#spinnerImage").remove();
    $('#submit_pointDialog').on('click', function(e){submitPointDialog(this);});
    $('#submit_pointDialog').show();
}

// This fucntion is weird in that it has to call some functions in point.js
// Oh god I'm sorry
function submitPointDialog(clickedElement) {
    var dialogAction = $(clickedElement).data('dialogaction');
    if (dialogAction == "new") {
        newPoint();
    } else if (dialogAction == "edit") {
        callPointEdit();
    } else if (dialogAction == "createLinked") {
        var linkType = $(clickedElement).data('linktype');
        addPoint(linkType);
    }
}

function removeSource(clickedElement) {
    var sourcekey = $(clickedElement).parent().data('sourcekey');
    if (sourcekey) {
        var sourcesToRemove = $('#pointDialog').data('sourcesToRemove');
        if(typeof sourcesToRemove == 'undefined') {
            sourcesToRemove = [];
        }
        sourcesToRemove.push(sourcekey);
        $('#pointDialog').data('sourcesToRemove', sourcesToRemove);
    }
    
    $(clickedElement).parent().remove();    
}

function updateDialogHeight() {
    numSources = $("[name='source_pointDialog']").length;
    if (numSources > 1) {
        $(".pointDialog").height(590 + (numSources-1)*20);        
    } else {
        $(".pointDialog").height(590);
    }
    
}

function addSource(clickedElement) {
    var urlVal = $('#sourceURL_pointDialog').val();
    if (urlVal == "") {
        editDialogAlert('URL is required');        
    } else if (!validateURL(urlVal)) {        
        editDialogAlert('The URL you specified doesn\'t look like a URL.');            
    } else {        
        sourceURL = $('#sourceURL_pointDialog').val();
        sourceTitle = $('#sourceTitle_pointDialog').val() == "" ? 
            sourceURL :$('#sourceTitle_pointDialog').val();        
        addSourceHTML(sourceURL, sourceTitle, null);  
        $('#sourceURL_pointDialog').val("");
        $('#sourceTitle_pointDialog').val("");
    }   
}

function addSourceHTML(sourceURL, sourceTitle, sourceKey) {
    
    appendAfter = $('#sourcesArea');
      
    newDiv = jQuery('<div/>',{ name:"source_pointDialog"} );
    newDiv.addClass("row-fluid");
    if (sourceKey != "") {
        newDiv.data('sourcekey', sourceKey);
    }
    newDiv.html("<a class=\"span2 offset1 removeSource\" href=\"#\">x</a>" + 
        "<a class=\"span9 sourceLink\" target=\"_blank\" href=\"" +  sourceURL+"\">"+ sourceTitle + "</a>");
    appendAfter.append(newDiv);        
    updateDialogHeight();
    $('.removeSource',newDiv).on('click', function(e) {removeSource(this);});
}

function toggleTabbedArea(selectedTab, tabbedAreaToShow) {
	$('.tab').removeClass('selectedTab');
	$(selectedTab).addClass('selectedTab');
	$('.tabbedArea').hide();
	$(tabbedAreaToShow).show();
}

function makePointsCardsClickable() {
    $( ".pointCard" ).click( function() {
        window.location.href=$(".pointTitle a", $(this)).attr('href');
    });
}

function loadPointList(listType, areaToLoad, selectedTab) {
    $(areaToLoad).html('<div id="historyAreaLoadingSpinner"><img src="/static/img/ajax-loader.gif" /></div>');
    toggleTabbedArea(selectedTab, areaToLoad);
    $.ajax({
    	url: '/getPointsList',
    	type: 'POST',
    	data: { 'type': listType },
    	success: function(data) {
    		$(areaToLoad).empty();
    		$(areaToLoad).html($.parseJSON(data));
    		makePointsCardsClickable();
    	},
    	error: function(data) {
    		$(areaToLoad).empty();
    		showAlert('<strong>Oops!</strong> There was a problem loading the points.  Please try again later.');
    	},
    }); 
}

function getSearchResults(searchTerms) {
  	$.ajaxSetup({
		url: "/search",
		global: false,
		type: "POST",
		data: {
			'searchTerms': searchTerms,		
		},
		success: function(data) {
            obj = JSON.parse(data);
		    if (obj.result == 0) {
		        showAlert("No results found for: <strong>" + obj.searchString + "</strong>");
		    } else {
		        $("#mainContainer").children().remove();
		        $("#mainContainer").append(obj.html);
		        makePointsCardsClickable();	                
		    }
		},
	});
	$.ajax();
}

function clearSignupDialog() {
    $("#signup_userName").val("");    
    $("#signup_userWebsite").val("");
    $("#signup_userAreas").val("");
    $("#signup_userProfession").val("");
    $("#signup_userBio").val("");
    $("#signup_userEmail").val("");    
    $("#signup_password1").val("");    
    $("#signup_password2").val("");   
    $(".alert").remove();
}

function validateSignupDialog() {
    valid = true;
    userName = $("#signup_userName").val();    
    websiteVal = $("#signup_userWebsite").val();
    areasVal = $("#signup_userAreas").val();
    professionVal = $("#signup_userProfession").val();
    bioVal = $("#signup_userBio").val();
    email = $("#signup_userEmail").val();    
    password1 = $("#signup_password1").val();    
    password2 = $("#signup_password2").val();    
    
    if (password1 != password2) {
        dialogAlert('#signupDialog','Oops. Your passwords do not match.');
        valid = false;
    } else if (password1.length < 8) {
        dialogAlert('#signupDialog','Please make your password 8 or more characters in length.');
        valid = false;
    } else if (!validatePassword(password1)) {
        dialogAlert('#signupDialog','Please include  at least one letter and at least one number in your passoword.');
        valid = false;
    }    
    if (userName.length >= 500) {
        dialogAlert('#signupDialog','Please do not exceed maximum length for Username (500 characters)');
        valid = false;
    } else if (userName.length <= 3) {
        dialogAlert('#signupDialog','Please specify a username at least four characters long.');
        valid = false;
    }
    if (professionVal.length >= 500) {
        dialogAlert('#signupDialog','Please do not exceed maximum length for Current Profession (500 characters)');
        valid = false;        
    }  
    if (websiteVal.length >= 500) {
        dialogAlert('#signupDialog','Please do not exceed maximum length for Website URL (500 characters)');
        valid = false;        
    }  
    if (areasVal.length >= 500) {
        dialogAlert('#signupDialog','Please do not exceed maximum length for Areas of Expertise (500 characters).  Wow, you must have a lot of expertise!');
        valid = false;        
    } 
    if (bioVal.length >= 500) {
        dialogAlert('#signupDialog','Please do not exceed maximum length for Username (500 characters)');
        valid = false;
    }
    if (websiteVal != '' && !validateURL(websiteVal)) {
        dialogAlert('#signupDialog','The Website URL you specified does not look like a valid URL');
        valid = false;
    }
    
    if (email == '') {
        dialogAlert('#signupDialog','Please enter a valid email address.');
        valid = false;
    } else if (!validateEmail(email)) {
        dialogAlert('#signupDialog','The Email URL you specified does not look like a valid email address');
        valid = false;
    }
    
    return valid;
}

function createNewUser() {
    if (validateSignupDialog()) {
        startSpinnerOnButton('#submit_signupDialog');
        $.ajaxSetup({
    		url: "/signup",
    		global: false,
    		type: "POST",
    		data: {
    		    'userName': $("#signup_userName").val(),
                'website':  $("#signup_userWebsite").val(),
                'areas': $("#signup_userAreas").val(),
                'profession': $("#signup_userProfession").val(),
                'bio': $("#signup_userBio").val(),
                'email': $("#signup_userEmail").val(),   
                'password':$("#signup_password1").val(),
    		},
            success: function(data){
    			obj = JSON.parse(data);
    			if (obj.result == true) { 
    			    stopSpinnerOnButton('#submit_signupDialog', createNewUser);
    			    clearSignupDialog();            
                    $("#signupDialog").modal('hide');                                           
                    showSuccessAlert('User created successfully. Please check your email for a validation message.');
    			} else {
    				if (obj.error) {
    		    		dialogAlert('#signupDialog',obj.error);
    		    	} else {
    		    		dialogAlert('#signupDialog',"There was an error");
    		    	}
                    stopSpinnerOnButton('#submit_signupDialog', createNewUser);            
    			}
    		},
    		error: function(xhr, textStatus, error){
                dialogAlert('#signupDialog','The server returned an error. You may try again. ' + error);
                stopSpinnerOnButton('#submit_signupDialog', createNewUser);            
            }
    	});
    	$.ajax();
        
    }    
}

function login() {
    $('#frm_emailLoginDialog').submit();
}

function validateForgotPassword() {
    valid = true;
    email = $("#login_userEmail").val();
    if (email == '') {
        dialogAlert('#emailLoginDialog','Please enter your login email address or username.');
        valid = false;
    }  
    return valid;
}

function forgotPassword() {
    if (validateForgotPassword() &&
        confirm("Send a password reset email to " + $("#login_userEmail").val() + "?  (Users with no email on file write to admin@whysaurus.com for a password reset.)")) {           
            startSpinnerOnButton('#forgot_emailLoginDialog');        
            $.ajaxSetup({
        		url: "/forgot",
        		global: false,
        		type: "POST",
        		data: {
        		    'email': $("#login_userEmail").val(),
        		},
                success: function(data){
        			obj = JSON.parse(data);
        			if (obj.result == true) { 
        			    stopSpinnerOnButton('#forgot_emailLoginDialog', forgotPassword);
                        $("#emailLoginDialog").modal('hide');  
                        if (obj.message) {
                            showAlert(obj.message);
                        } else {
                            showSuccessAlert('We have sent an email with a password reset link to your email address.');                        
                        }                
        			} else {
                        dialogAlert('#emailLoginDialog', obj.error ? obj.error : "There was an error");
                        stopSpinnerOnButton('#forgot_emailLoginDialog', forgotPassword);            
        			}
        		},
        		error: function(xhr, textStatus, error){
                    dialogAlert('#emailLoginDialog','The server returned an error. You may try again. ' + error);
                    stopSpinnerOnButton('#forgot_emailLoginDialog', forgotPassword);            
                }
        	});
            $.ajax();
    }
}

function initTinyMCE() {
    
    tinyMCE.init({
      // General options
      mode: "specific_textareas",
      theme: "advanced",
      editor_selector: "mceEditor",
      editor_deselector: "mceNoEditor",
      content_css : '/static/css/content.css',
      paste_text_sticky: true,
      paste_text_sticky_default: true,
      plugins: "autolink,lists,spellchecker,iespell,inlinepopups,noneditable,paste",
      // Theme options
      theme_advanced_buttons1: "bold,italic,underline,|,sub,sup,bullist,numlist,blockquote,|,undo,redo,|,link,unlink,spellchecker",
      theme_advanced_buttons2: "",
      theme_advanced_buttons3: "",
      theme_advanced_buttons4: "",
      theme_advanced_toolbar_location: "top",
      theme_advanced_toolbar_align: "left",
      theme_advanced_statusbar_location: "none",
      theme_advanced_resizing: true,
      theme_advanced_resizing_use_cookie : false,
      height : "60px",
      // Skin options
      skin: "o2k7",
      skin_variant: "silver",
      // Drop lists for link/image/media/template dialogs
      template_external_list_url: "js/template_list.js",
      external_link_list_url: "js/link_list.js",
      external_image_list_url: "js/image_list.js",
      media_external_list_url: "js/media_list.js",
    });
}

function switchArea() {
    $.ajaxSetup({
		url: "/switchArea",
		global: false,
		type: "POST",
		data:{},
        success: function(data){
			obj = JSON.parse(data);
			if (obj.result == true) { 
                window.location.href="/";                
			} else {
			    showAlert("Something went wrong. Not able to change area.");
			}
		},
		error: function(xhr, textStatus, error){
		    showAlert("There was an error. Not able to change area. " + textStatus);       
        }
	});
	$.ajax();
}

function processNotification(messageObj) {
     
     var dataObj = JSON.parse(messageObj.data);
     
     // Insert new notification
     $('#notificationMenuHeader').after(dataObj.notificationHTML);
     
     // Update the number
     count = parseInt($('#notificationCount').text());
     count = count + 1;
     $('#notificationCount').text(count.toString());
     $('#notificationCount').show();
          
     // Insert the raised date secs value
     $('#notificationMenuHeader').data('latest', dataObj.timestamp)         
     
}

function reconnectChannel(errorObj) {
    if (channelErrors > 2) {
         showAlert('Cannot receive notifications. Error was: ' + errorObj.description + ' Code: ' + errorObj.code);        
     } else {
         try {
             channelErrors = channelErrors + 1;            
         } catch (err) {
             alert(err.message);
         }
         try {
             $.ajaxSetup({
            		url: "/newNotificationChannel",
            		global: false,
            		type: "POST",           		
                 success: function(data) {
            			obj = JSON.parse(data);
            			if (obj.result == true) { 
            			    channelToken = obj.token;
            			    notificationChannelOpen();
            			} else {
            			    showAlert("Could not request notification channel.  Cannot receive notifications.");
            			}
            		},
            		error: function(xhr, textStatus, error){
            		    showAlert("Error connecting to notification channel: " + textStatus);       
                 },
            	}); 
         } catch (err) {
             alert("2" + err.message);            
         }
         $.ajax();        
     }    
}

function notificationChannelOpen() {
    if (typeof(channelToken) != "undefined") {
        lastNotiSecs = $("#notificationMenuHeader").data('latest');
        channel = new goog.appengine.Channel(channelToken);
        socket = channel.open();
        socket.onmessage = processNotification;
        socket.onclose = reconnectChannel;
    }
  
}


function markNotificationsRead() {
    latest = $('#notificationMenuHeader').data('latest');
    earliest = $('#notificationMenuHeader').data('earliest');
    if (typeof(latest) != "undefined") {
        $.ajaxSetup({
        	url: "/clearNotifications",
        	global: false,
        	type: "POST",  
        	data:{
        	    'latest':latest,
        	    'earliest':earliest
        	},         		
            success: function(data) {
                obj = JSON.parse(data);
        		if (obj.result == true) {
                    $('#notificationCount').text(0);
                    $('#notificationCount').hide();
                } else {
                    console.log('CleanNotifications call returned error: ' + obj.error);        	    
                }            
        	},
        	error: function(xhr, textStatus, error){
        	    console.log('Error clearing notifications: ' + textStatus);
            },
        });
        $.ajax();
    }
}

function makeNotificationMenuClickable() {
    $('.notificationMenuItem').click( function() {
        window.location.href=$(this).data('refpoint');        
    });
    
    $('#notificationMenuHeader').click(function () {
        window.location.href=userURL;                
    });
    
    $('#notificationMenuFooter').click(function () {
        window.location.href=userURL;                
    });
    
    $('#notifications').click(markNotificationsRead);
}


var channelErrors = 0; 
var FILEPICKER_SERVICES = ['IMAGE_SEARCH', 'COMPUTER', 'URL', 'FACEBOOK'];

$(document).ready(function() {
  filepicker.setKey("AinmHvEQdOt6M2iFVrYowz");
  $.fn.bindFilepicker = function(){
    if (this.bindFilepickerBound) return;
    this.bindFilepickerBound = true;
    this.click(function(){
      var self = this;
      filepicker.pickAndStore(
        { mimetype:"image/*", services: FILEPICKER_SERVICES, openTo: 'IMAGE_SEARCH' },
        { location: "S3" },
        function(fpfiles){
          var file = fpfiles[0];

          $('.filepicker-placeholder').attr('src', '/static/img/icon_triceratops_black_47px.png').addClass('spin');

          filepicker.convert(file, {width: 112, height: 112, fit: 'clip'}, {path: 'SummaryBig-' + file.key});
          filepicker.convert(file, {width: 310, fit: 'clip'}, {path: 'FullPoint-' + file.key});
          filepicker.convert(file, {width: 54, height: 54, fit: 'clip'}, {path: 'SummaryMedium-' + file.key}, function(medium){
            $('.filepicker-placeholder')
              .attr('src', 'http://d3uk4hxxzbq81e.cloudfront.net/' + encodeURIComponent(medium.key))
              .removeClass('spin');
          });

          $(self).prev('[name=imageURL]').val(file.key);
        }
      );

      return false;
    });
  };

  $('#pointDialog .filepicker').bindFilepicker();

  $("#searchBox").keyup(function(event) {
    if (event.keyCode == 13) {
        getSearchResults($("#searchBox").val());
    }
  });
  
  $(".searchIcon", $("#searchArea")).click(function(event) {
    if ($("#searchBox").val() != "") {
        getSearchResults($("#searchBox").val());
    }
  });

  initTinyMCE();

    $('[id^="signInWithFacebook"]').click(function() {
        window.location.href = "/auth/facebook";
    });

    $('[id^="signInWithGoogle"]').click(function() {
        window.location.href = "/auth/google";
    });

    $('[id^="signInWithTwitter"]').click(function() {
        window.location.href = "/auth/twitter";
    });
    
    /*window.onload = function() {
        positionEditDialog();
    };
    window.onresize = function() {
        positionEditDialog();
    };*/

    // Beginning state for the TABBED AREAS
    $('.tabbedArea').hide(); $('#recentActivityArea').show();

    $('#recentActivity').click(function() {
        toggleTabbedArea(this, "#recentActivityArea");        
    });

    $('#editorsPicks').click(function() {
        loadPointList('editorsPics', '#editorsPicksArea', this);        
    });
    
    $('#mostViews').click(function() {
        loadPointList('topViewed', '#mostViewsArea', this);
    });
    
    $('#mostCaps').click(function() {
        loadPointList('topAwards', '#mostCapsArea', this);
    });
    
    $('#mostAgrees').click(function() {
        loadPointList('topRated', '#mostAgreesArea', this);
    });
    
    
    
    makePointsCardsClickable();	
    $( "#recentlyViewed .pointSmall" ).click( function() {
        window.location.href=$(".smallTitle a", $(this)).attr('href');
    });
       
    if (!loggedIn) {
        $("#CreatePoint").attr('href', "#loginDialog");
        $("#CreatePoint").attr('data-toggle', "modal");
        $("#loginWithEmail").on('click', function() {
            $("#emailLoginDialog").modal('show');
        });
        $("#showSignupDialog").on('click', function() {
            $("#emailLoginDialog").modal('hide');
            $("#signupDialog").modal('show')            
        });
        
        $("#signInWithEmail_Dlg").on('click', function() {
            $("#loginDialog").modal('hide');
            $("#emailLoginDialog").modal('show');           
        });
        
        $("#backToLogin").on('click', function() {
            $("#signupDialog").modal('hide');                       
            $("#loginDialog").modal('show');
        });
        
        $('#submit_signupDialog').click( createNewUser );
        $('#submit_emailLoginDialog').click( login );    
        $('#forgot_emailLoginDialog').click( forgotPassword );        
                                  
    } else {
        $( "#CreatePoint" ).on('click', function() {
            $("#submit_pointDialog").data("dialogaction", "new");
            $('div.modal-header h3', $('#pointDialog')).text("New Point");
            $("#pointDialog").modal('show');
        });

        $("#pointDialog").on('hidden', function() {
          var edSummary = tinyMCE.get('editor_pointDialog');
          edSummary.setContent('');
          $('#title_pointDialog').val('');
          setCharNumText($('#title_pointDialog')[0]);
          $('#link_pointDialog').val('');
          $('#author_pointDialog').val('');
          $('#description_pointDialog').val('');
          $('.filepicker-placeholder').attr('src', "/static/img/placeholder_50x50.gif");
          $('[name=source_pointDialog]').remove();
          $('#pointDialog').removeData('sourcesToRemove');     
          $('#sourceURL_pointDialog').val("");
          $('#sourceTitle_pointDialog').val("");
   
        });
        
        $("#pointDialog").on('shown', function() {
            $('#title_pointDialog').focus();
        });

        $("#submit_pointDialog").on('click', function(e) {
            submitPointDialog(this);
        });

        $("#sourcesAdd").on('click', function(e) {
            e.preventDefault();
            addSource(this);
        });

        $("#title_pointDialog").on('keyup', function(e) {setCharNumText(e.target);});

        $(".removeSource").on('click', function(e) {removeSource(this);});
        $("#areaSwap").on('click', switchArea);   
        makeNotificationMenuClickable();     
        notificationChannelOpen();
    }
    
    // Unsupported browser alert
    
    var isOpera = !!window.opera || navigator.userAgent.indexOf(' OPR/') >= 0;
    var isChrome = !!window.chrome && !isOpera;         
    if (isChrome == false) {
        showAlert('You are using Whysaurus in a unsupported browser.  We are in Beta and only Chrome is supported for now.');
    }


  //Add Hover effect to menus.  Well, it doesn't work very well...
  // But on the off chance we decide to put it back later. . .
 /*  jQuery('div.userControls a.dropdown-toggle').hover(function() {
    $('.dropdown-menu').stop(true, true).delay(200).fadeIn();
  }, function() {
    $('.dropdown-menu').stop(true, true).delay(200).fadeOut();
  });
  */
});
