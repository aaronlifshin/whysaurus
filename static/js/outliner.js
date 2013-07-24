var pointIdx = 0;

function newInput(level) {
    pointIdx = pointIdx + 1;
    return("<div class=\"row span6\"><input class=\"outlinerInput level" + level + "\" data-level=\"" + level + "\" data-ref=\"" + pointIdx + "\"/></div>");
}

function deleteOutlinePoint(textbox) {
    var lvl = $(this).data('level');    
    if (lvl != 0 ) {
        var forFocus = $(":first-child",$(textbox).parent().prev());
        $(textbox).remove();
        forFocus.get(0).focus();
    }
}



function shiftRight(textbox) {
    var lvl = $(textbox).data('level');
    var prevLvl = $(":first",$(textbox).parent().prev()).data('level');
    
    if (lvl > 4) {
        showAlert('maxLevelReached');
    } else if (lvl - prevLvl < 1){
        var newLevel = lvl + 1;
        $(textbox).removeClass('level' + lvl);
        $(textbox).addClass('level' + newLevel);        
        $(textbox).data('level', lvl + 1);
    }
}

function shiftLeft(textbox) {
    var lvl = $(textbox).data('level');
    if (lvl > 1) {
        var newLevel = lvl - 1;        
        $(textbox).removeClass('level' + lvl);
        $(textbox).addClass('level' + newLevel);
        $(textbox).data('level', lvl - 1);
    }
}

function outlinerKeyup(event) {
    var lvl = $(this).data('level');    
    if (event.keyCode == 13) {       
      if (lvl == 0) {
          newRow = $(this).parent().after(newInput(1));      
      } else {
          newRow = $(this).parent().after(newInput(lvl));                        
      }
      setOutlinerEvents();
      $(":first-child",newRow.next()).get(0).focus();      
    } else if ((event.keyCode == 8 || event.keyCode == 46) // TODO: ??check for children here also??
                && $(this).val() == "" && lvl != 0) {
        deleteOutlinePoint(this);
    }
}

function outlinerKeydown(event) {
    var lvl = $(this).data('level');
    var prevLvl = $(":first",$(this).parent().prev()).data('level');
  
    if (event.keyCode == 9 && event.shiftKey && lvl != 0) {
        event.preventDefault();    
        shiftLeft(this);

    } else if (event.keyCode == 9 && lvl != 0) { 
        event.preventDefault();             
        shiftRight(this);
    }
}

function setOutlinerEvents() {
    // Make sure there is only one
    $(".outlinerInput").unbind("keyup", outlinerKeyup);   
    $(".outlinerInput").unbind("keydown", outlinerKeydown);       
        
    $(".outlinerInput").on("keyup", outlinerKeyup);
    $(".outlinerInput").on("keydown", outlinerKeydown);
    
}

function saveOutlinerPoint(textbox, rowNum) {
    // Find the parent point
    var parentURL = '';
    var level = $(textbox).data('level');
    $(".outlinerInput", $(textbox).parent().prevAll()).each(function (index, element) {
         tb = $(element);
            if (tb.data('level') < level) {
                parentURL = tb.data('url');
            }
    });
    if (parentURL == '') {
        showAlert('There was an error: URL of previous point not set when expected.')
        return;
    }
    $(textbox).parent().after("<img id=\"spinnerImage" + rowNum +"\" src=\"/static/img/ajax-loader.gif\"/>");  
    $.ajaxSetup({
        url: "/addSupportingPoint",
        global: false,
        type: "POST",
        data: {
            'content': '',
            'plainText': '',
            'title': $(textbox).val(),
            'linkType':'supporting',
			'pointUrl': parentURL,
            'imageURL': '',
            'imageAuthor': '',
            'imageDescription': '',
            'sourcesURLs': JSON.stringify([]),
            'sourcesNames': JSON.stringify([])
        },
        success: function(data) {
            obj = JSON.parse(data);
            $("#spinnerImage" + rowNum).remove();   
            if (obj.result === true) {
                $(textbox).parent().after("<img id=\"greenCheck" + rowNum + "\" src=\"/static/img/greenCheck.jpeg\"/>");                                                                                           
                $(textbox).data('url',  obj.pointURL);
                // It will bottom out because level is limited, but just in case
                if (level < 5) {
                    saveOutlinerPoint($(".outlinerInput", $(textbox).parent().nextAll())[0], rowNum+1);                    
                }
            } else {
                showAlert('Could not save main point: ' + obj.error);
            }
        },
        error: function(xhr, textStatus, error) {
            showAlert('The server returned an error. You may try again.');
            $("#spinnerImage0").remove();            
        }
    });
    $.ajax();   
    
}


function getPointData() {
    var points  = $('.outlinerInput');
    var titles = []; 
    var levels = []; 
    var dataRefs = []; 

    for(var i = 0; i < points.length; i++){
        titles.push($(points[i]).val());
        levels.push($(points[i]).data('level'));
        dataRefs.push($(points[i]).data('ref'));
    }
    return [titles,levels,dataRefs];
}

function saveMainPoint(textbox) {
    $(textbox).parent().after("<img id=\"spinnerImage0\" src=\"/static/img/ajax-loader.gif\"/>"); 
    pointData = getPointData();
    $.ajaxSetup({
        url: "/addTree",
        global: false,
        type: "POST",
        data: {
            'titles': JSON.stringify(pointData[0]),
            'levels': JSON.stringify(pointData[1]),
            'dataRefs': JSON.stringify(pointData[2]),
        },
        success: function(data) {
            obj = JSON.parse(data);
            $("#spinnerImage0").remove();   
            if (obj.result === true) {
                $(textbox).parent().after("<img id=\"greenCheck0\" src=\"/static/img/greenCheck.jpeg\"/>");                                                                           
                var params = [];
                params["rootKey"] = obj.rootKey;
                post_to_url("/point/" +  obj.url, params);
            } else {
                showAlert('Could not save main point: ' + obj.error);
            }
        },
        error: function(xhr, textStatus, error) {
            showAlert('The server returned an error. You may try again.');
            $("#spinnerImage0").remove();            
        }
    });
    $.ajax();
}

function saveOutline() {
    titleFields  = $('.outlinerInput');
    
    if (confirm('Going to save ' + titleFields.length + ' points.  Are you sure?')) {  
        for(ind in titleFields){
          titleField = titleFields[ind];
          if (ind == 0) {
             saveMainPoint(titleField);
          }
          //do whatever you want
        }        
    }

}

$(document).ready(function() {
    setOutlinerEvents();
    $("#saveOutline").on("click", saveOutline)
});
