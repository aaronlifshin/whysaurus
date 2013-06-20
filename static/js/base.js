var CONST_EDITOR_DEFAULT_TEXT = 'Add the description here...';
var MAX_TITLE_CHARS = 140;

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
};

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


function positionEditDialog() {
  dialogHeight = $(".pointDialog").height();
  $("[id$='_ifr']").height(dialogHeight - 350);
}

function newPoint() {
  if ($('#title_pointDialog').val().length > MAX_TITLE_CHARS) {
      alert('Too many characters in the title');
      return;
  }
  var ed = tinyMCE.get('editor_pointDialog');
  var text = tinyMCE.activeEditor.getBody().textContent;
  $("#submit_pointDialog").off('click');
  $("#submit_pointDialog").hide();
  $("#submit_pointDialog").after("<img id=\"spinnerImage\" src=\"/static/img/ajax-loader.gif\"/>");

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
      'imageDescription': $('#description_pointDialog').val()
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
        editDialogAlert('The server returned an error. You may try again.');
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

function editDialogAlert(alertHTML) {
    $('#pointDialog #alertArea').html($('<div class="alert"><button type="button" class="close" data-dismiss="alert">&times;</button>' + alertHTML + '</div>'));
}

function stopSpinner() {
    $("#spinnerImage").remove();
    $('#submit_pointDialog').on('click', function(e){submitPointDialog(this);});
    $('#submit_pointDialog').show();
}

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

var FILEPICKER_SERVICES = ['COMPUTER', 'URL', 'FACEBOOK'];
$(document).ready(function() {


  filepicker.setKey("AinmHvEQdOt6M2iFVrYowz");
  $.fn.bindFilepicker = function(){
    if (this.bindFilepickerBound) return;
    this.bindFilepickerBound = true;
    this.click(function(){
      var self = this;
      filepicker.pickAndStore(
        { mimetype:"image/*", services: FILEPICKER_SERVICES, openTo: 'COMPUTER' },
        { location: "S3" },
        function(fpfiles){
          var file = fpfiles[0];

          $(self).next('.filepicker-placeholder').attr('src', '/static/img/icon_triceratops_black_47px.png').addClass('spin');

          filepicker.convert(file, {width: 112, height: 112, fit: 'clip'}, {path: 'SummaryBig-' + file.key});
          filepicker.convert(file, {width: 310, fit: 'clip'}, {path: 'FullPoint-' + file.key});
          filepicker.convert(file, {width: 54, height: 54, fit: 'clip'}, {path: 'SummaryMedium-' + file.key}, function(medium){
            $(self)
              .next('.filepicker-placeholder')
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


  tinyMCE.init({
    // General options
    mode: "specific_textareas",
    theme: "advanced",
    editor_selector: "mceEditor",
    editor_deselector: "mceNoEditor",
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
    theme_advanced_resizing: false,
    // Skin options
    skin: "o2k7",
    skin_variant: "silver",
    // Drop lists for link/image/media/template dialogs
    template_external_list_url: "js/template_list.js",
    external_link_list_url: "js/link_list.js",
    external_image_list_url: "js/image_list.js",
    media_external_list_url: "js/media_list.js",
    /*setup: function(ed) {
        // All this to try deal with placeholder text
        // Could not get it to work for gaining focus when
        // tabbing into the editor BLEH
        var tinymce_placeholder = $('#createPointDialog');

        ed.onInit.add(function(ed) {
            // get the current content
            var cont = ed.getContent();
            // If its empty and we have a placeholder set the value
            if(cont.length == 0){
               ed.setContent(CONST_EDITOR_DEFAULT_TEXT);
            }
        });

        ed.onMouseDown.add(function(ed,e) {
            clearDefaultContent(ed);
        });

        ed.onNodeChange.add(function(ed,e) {
            clearDefaultContent(ed);
        });
      } */
  });


  $("#searchBox").keyup(function(event) {
    if (event.keyCode == 13) {
      window.location.href = "/search?searchTerms=" + $("#searchBox", $("#searchArea")).val();
    }
  });

  $(".searchIcon", $("#searchArea")).click(function(event) {
    if ($("#searchBox").val() !== "") {
      window.location.href = "/search?searchTerms=" + $("#searchBox", $("#searchArea")).val();
    }
  });


  // Dialog form handling
  /*$("#dialogForm").dialog({
    autoOpen: false,
    height: getWindowHeight() * .9,
    width: $(window).width()*.7,
    modal: true
  });

  if (!loggedIn) {
    $("#loginDialog").dialog({
      autoOpen: false,
      height: 250,
      width: 270,
      modal: true
    });
  }*/

  $('[id^="point_New_"]').click(function() {
      window.location.href = $(".navWhy", $(this)).attr('href');
  });

  $('[id^="signInWithFacebook"]').click(function() {
      window.location.href = "/auth/facebook";
  });

  $('[id^="signInWithGoogle"]').click(function() {
      window.location.href = "/auth/google";
  });

  $('[id^="signInWithTwitter"]').click(function() {
      window.location.href = "/auth/twitter";
  });
  window.onload = function() {
    positionEditDialog();
  };
  window.onresize = function() {
    positionEditDialog();
  };

  if (!loggedIn) {
    $("#CreatePoint").attr('href', "#loginDialog");
    $("#CreatePoint").attr('data-toggle', "modal");
  } else {

    $( "#CreatePoint" ).on('click', function() {
        $("#submit_pointDialog").data("dialogaction", "new");
        $('div.modal-header h3').text("New Point");
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
    });

    $("#submit_pointDialog").on('click', function(e) {
        submitPointDialog(this);
    });

    $("#title_pointDialog").on('keyup', function(e) {setCharNumText(e.target);});


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
