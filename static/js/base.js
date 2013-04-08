var CONST_EDITOR_DEFAULT_TEXT = 'Add the description here...';

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
  var ed = tinyMCE.get('editor_createPointDialog');
  var text = tinyMCE.activeEditor.getBody().textContent;
  $.ajaxSetup({
    url: "/newPoint",
    global: false,
    type: "POST",
    data: {
      'content': ed.getContent(),
      'plainText': text.substring(0, 250),
      'title': $('#title_createPointDialog').val(),
      'imageURL': $('#link_createPointDialog').val(),
      'imageAuthor': $('#author_createPointDialog').val(),
      'imageDescription': $('#description_createPointDialog').val()
    },
    success: function(data) {
      obj = JSON.parse(data);
      if (obj.result === true) {
        window.location.href = "/point/" + obj.pointURL;
      } else {
        alert(obj.result);
      }
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

var FILEPICKER_SERVICES = ['COMPUTER', 'URL', 'FACEBOOK'];
$(document).ready(function() {
  filepicker.setKey("AinmHvEQdOt6M2iFVrYowz");
  $.fn.bindFilepicker = function(){
    this.click(function(){
      var self = this;
      filepicker.pickAndStore(
        { mimetype:"image/*", services: FILEPICKER_SERVICES, openTo: 'COMPUTER' },
        { location: "S3" },
        function(fpfiles){
          var file = fpfiles[0];

          $(self).next('.filepicker-placeholder').attr('src', '/static/img/icon_triceratops_white_47px.png').addClass('spin');

          filepicker.convert(file, {width: 112, height: 112, fit: 'clip'}, {path: 'SummaryBig-' + file.key});
          filepicker.convert(file, {width: 310, fit: 'clip'}, {path: 'FullPoint-' + file.key});
          filepicker.convert(file, {width: 54, height: 54, fit: 'clip'}, {path: 'SummaryMedium-' + file.key}, function(medium){
            $(self).next('.filepicker-placeholder').attr('src', 'http://d3uk4hxxzbq81e.cloudfront.net/' + medium.key).removeClass('spin');
          });

          $(self).prev('[name=imageURL]').val(file.key);
        }
      );

      return false;
    });
  };

  $('#frm_createPointDialog .filepicker, #createSupportingPoint .filepicker').bindFilepicker();

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

  $(".pointSmall").click(function() {
    if (!$(".navWhy", $(this)).hasClass("ui-helper-hidden")) { // In the point page the navWhy is sometimes hidden by the unlink button
      window.location.href = $(".navWhy", $(this)).attr('href');
    }
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
    $("#CreatePoint").attr('href', "#createPointDialog");
    $("#CreatePoint").attr('data-toggle', "modal");
    $("#createPointDialog").on('hidden', function() {
      var edSummary = tinyMCE.get('editor_createPointDialog');
      edSummary.setContent('');
      $('#title_createPointDialog').val('');
      $('#link_createPointDialog').val('');
      $('#author_createPointDialog').val('');
      $('#description_createPointDialog').val('');
    });
    $("#submit_createPointDialog").on('click', function(e) {
      e.preventDefault();
      newPoint();
      $("#createPointDialog").hide();
    });
  }

});
