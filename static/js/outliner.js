var pointIdx = 0;

function newInput(level) {
    pointIdx = pointIdx + 1;
    newHtml = "<div class=\"row outlinerRow\"><div class=\"span6\"><input id=\"pointInput_"  + pointIdx +  
        "\" class=\"outlinerInput level" + level + 
        "\" data-level=\"" + level + "\" data-ref=\"" + pointIdx + "\"/></div>" +
        "<div class=\"span1\">" +
            "<img id=\"outliner_addBelow_" + pointIdx + "\" src=\"/static/img/green-plus.png\"/>" +
            "<img id=\"outliner_left_" + pointIdx + "\" src=\"/static/img/arrow-left.png\"/> " +
            "<img id=\"outliner_right_" + pointIdx + "\" src=\"/static/img/arrow-right.png\"/> " +
            "<img id=\"outliner_delete_" + pointIdx + "\" src=\"/static/img/red-x.png\"/> " +          
        "</div></div>";
    return newHtml;
}

function newDetailArea(reference) {
    newHtml = "<div id=\"outliner_detailArea_" + reference + "\" data-ref=\"" + reference + "\">" +
        "<div>Add Details To Your Point Here</div>" +   
        "<div class=\"pull-right\" id=\"pointInput_" + reference +"_charNum\" + data-ref=\""+ reference +
        "\">140 characters remaining</div>" +                                       
        "<textarea class=\"repeatTitle\" id=\"outliner_Title_" + reference +  
            "\" data-ref=\"" + reference +  "\"></textarea>" +
        "<div>Additional Text</div>" +
        "<textarea class=\"furtherInfo\" id=\"outliner_FurtherInfo_"+ reference + 
            "\" data-ref=\"" + reference + "\"></textarea>" +
        "<div id=\"outliner_sources_"+ reference + "\" data-ref=\"" + reference + 
        "\">Sources</div> Title: <input id=\"outliner_SourceTitle_"+ 
        reference + "\" data-ref=\"" + reference + 
        "\"/><br>URL: <input id=\"outliner_SourceURL_"+ reference + "\" data-ref=\"" + reference + 
        "\"/><br><button class=\"pull-right\" id=\"outliner_addSource_"+ reference + "\" data-ref=\"" + reference + 
        "\">Add Source</button> </div>"
    return newHtml;
}

function newOutlinerSource(sourceURL, sourceTitle, reference) {
    appendAfter = $('#outliner_sources_' + reference);
    
    newDiv = jQuery('<div/>',{class:"row-fluid", name:"outliner_source_" + reference} );
    newDiv.data('ref', reference);
    newDiv.html("<a class=\"span1 removeSource\" href=\"#\">x</a>" + 
        "<a class=\"span11 sourceLink\" target=\"_blank\" href=\"" +  sourceURL+"\">"+ sourceTitle + "</a>");
    appendAfter.append(newDiv);        
    $('.removeSource',newDiv).on('click', function(e) {$(this).parent().remove()});    
}

function btnAddSource() {
    var ref = $(this).data('ref');
    var urlVal = $('#outliner_SourceURL_' + ref).val();
    if (urlVal == "") {
        showAlert('URL is required to add a source');        
    } else if (!validateURL(urlVal)) {        
        showAlert('The URL you specified doesn\'t look like a URL. Full URL, including http:// is needed to add a source.');            
    } else {        
        sourceURL = urlVal;
        sourceTitle = $('#outliner_SourceTitle_' + ref).val() == "" ? 
            sourceURL :$('#outliner_SourceTitle_' + ref).val();        
        newOutlinerSource(sourceURL, sourceTitle, ref);  
        $('#outliner_SourceURL_' + ref).val("");
        $('#outliner_SourceTitle_' + ref).val("");
    }
}

function btnDeleteOutlinePoint() {
    deleteOutlinePoint($(".outlinerInput",$(this).parent().parent()).get());
}

function deleteOutlinePoint(textbox) {
    var lvl = $(textbox).data('level');    
    var ref = $(textbox).data('ref');        
    if (lvl != 0 ) {
        var forFocus = getPreviousTitleField(textbox);
        $(textbox).parent().parent().remove();
        $("#outliner_detailArea_" + ref).remove();        
        forFocus.focus();
    }
}

function getPreviousTitleField(textbox) {
    return $(".outlinerInput",$(textbox).parent().parent().prev()).get(0);
}

function getNextTitleField(textbox) {
    return $(".outlinerInput",$(textbox).parent().parent().next()).get(0);
}

function btnShiftRight() {
    shiftRight($(".outlinerInput",$(this).parent().parent()).get());
}

function shiftRight(textbox) {
    var lvl = $(textbox).data('level');
    var prevLvl = $(getPreviousTitleField(textbox)).data('level');
    
    if (lvl > 4) {
        showAlert('You have reached the maximum depth level (5) and cannot indent further.  Sorry.');
    } else if (lvl - prevLvl < 1){
        var newLevel = lvl + 1;
        $(textbox).removeClass('level' + lvl);
        $(textbox).addClass('level' + newLevel);        
        $(textbox).data('level', lvl + 1);
    }
}

function btnShiftLeft() {
    shiftLeft($(".outlinerInput",$(this).parent().parent()).get());
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

function btnAddOutlinePoint() {
    addOutlinePoint($(".outlinerInput",$(this).parent().parent()).get());
}

function addOutlinePoint(textbox) {
    var lvl = $(textbox).data('level');        
    if (lvl == 0) {
        newRow = $(textbox).parent().parent().after(newInput(1));      
    } else {
        newRow = $(textbox).parent().parent().after(newInput(lvl));                        
    }
    $("#outliner_details").append(newDetailArea(pointIdx));
    setOutlinerEvents();
    $(".outlinerInput",newRow.next()).get(0).focus();
}


function outlinerKeyup(event) {
    var lvl = $(this).data('level');    
    if (event.keyCode == 13) {    // CREATE NEW POINT BELOWTHE CURRENT   
        addOutlinePoint(this);
    } else if (event.keyCode == 8 || event.keyCode == 46) { // TODO: ??check for children here also??
        if ($(this).val() == "" && lvl != 0) {
            deleteOutlinePoint(this);            
        } else if (getCaretPosition(this) == 0) {
            shiftLeft(this);
        }
    } else if (event.keyCode == 38) { // up arrow
        forFocus = getPreviousTitleField(this);
        if (forFocus) {
            forFocus.focus(); 
        }       
    } else if (event.keyCode == 40) { // down arrow
        forFocus = getNextTitleField(this);
        if (forFocus) {
            forFocus.focus(); 
        }
    } 
    var ref =  $(this).data('ref');
    $("#outliner_Title_" + ref).val($(this).val());
    setCharNumText(event.target);
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
    } else if ((event.keyCode == 8 || event.keyCode == 46) && event.shiftKey && lvl != 0) {
        deleteOutlinePoint(this);        
    }
}

function repeatTitleCopy() {
    var ref =  $(this).data('ref');
    $("#pointInput_" + ref).val($(this).val());
}

function outlinerFocus() {
    var ref = $(this).data('ref')
    $("[id^='outliner_detailArea_']").filter(':visible').hide();
    $("#outliner_detailArea_" + ref).show();
    
    $(".outlinerRow").removeClass('highlighted');
    $(this).parent().parent().addClass('highlighted');
                                  
}

function setOutlinerEvents() {
    // Make sure there is only one
    $(".outlinerInput").unbind("keyup", outlinerKeyup);   
    $(".outlinerInput").unbind("keydown", outlinerKeydown); 
    $(".outlinerInput").unbind("focus", outlinerFocus);
             
    $(".outlinerInput").on("keyup", outlinerKeyup);
    $(".outlinerInput").on("keydown", outlinerKeydown);
    $(".outlinerInput").on("focus", outlinerFocus);
    
    $(".repeatTitle").unbind("keyup", repeatTitleCopy);    
    $(".repeatTitle").on("keyup", repeatTitleCopy);
      
    $("[id^='outliner_addBelow']").unbind("click",btnAddOutlinePoint);
    $("[id^='outliner_left']").unbind("click",btnShiftLeft);
    $("[id^='outliner_right']").unbind("click",btnShiftRight);
    $("[id^='outliner_delete']").unbind("click",btnDeleteOutlinePoint);
    $("[id^='outliner_addSource_']").unbind("click",btnAddSource);
    
    $("[id^='outliner_addBelow']").on("click",btnAddOutlinePoint);
    $("[id^='outliner_left']").on("click",btnShiftLeft);
    $("[id^='outliner_right']").on("click",btnShiftRight);
    $("[id^='outliner_delete']").on("click",btnDeleteOutlinePoint);
    $("[id^='outliner_addSource_']").on("click",btnAddSource);           
}

function getSourcesData() {
    var sourceElems = $('[name^=outliner_source_]');
    var sources = []; 
    
    for(var i = 0; i < sourceElems.length; i++){
        sourceLink = $('.sourceLink', $(sourceElems[i]));
        source = {
            'ref':$(sourceElems[i]).data('ref'),
            'sourceURL':sourceLink.attr('href'),
            'sourceTitle':sourceLink.text(),
        };
        sources.push(source);
    }
    return sources;
}

function getPointData() {
    var points  = $('.outlinerInput');
    var titles = []; 
    var furtherInfos = [];    
    var levels = []; 
    var dataRefs = []; 

    for(var i = 0; i < points.length; i++){
        titles.push($(points[i]).val());
        levels.push($(points[i]).data('level'));
        var ref = $(points[i]).data('ref');
        dataRefs.push(ref);
        furtherInfos.push($("#outliner_FurtherInfo_" + ref).val())
    }
    return [titles,levels,dataRefs, furtherInfos];
}

function saveMainPoint() {
    $("#saveOutline").after("<img id=\"spinnerImage\" src=\"/static/img/ajax-loader.gif\"/>"); 
    pointData = getPointData();
    sources = getSourcesData();
    $.ajaxSetup({
        url: "/addTree",
        global: false,
        type: "POST",
        data: {
            'titles': JSON.stringify(pointData[0]),
            'levels': JSON.stringify(pointData[1]),
            'dataRefs': JSON.stringify(pointData[2]),
            'furtherInfos': JSON.stringify(pointData[3]),  
            'sources': JSON.stringify(sources)  
        },
        success: function(data) {
            obj = JSON.parse(data);
            $("#spinnerImage0").remove();   
            if (obj.result === true) {
                var params = [];
                params["rootKey"] = obj.rootKey;
                post_to_url("/point/" +  obj.url, params);
            } else {
                showAlert('Could not save main point: ' + obj.error);
            }
        },
        error: function(xhr, textStatus, error) {
            showAlert('The server returned an error. You may try again.');
            $("#spinnerImage").remove();            
        }
    });
    $.ajax();
}

function validateInputs() {
    var titleError = false;
    
    // All titles must exist
    titleFields  = $('.outlinerInput').each(function(i, obj){
        if ($(this).val() == '') {
            showErrorAlert('Cannot save: empty title at row ' + (i+1)); 
            titleError = true;                                       
        }        
        if ($(this).val().length > MAX_TITLE_CHARS) {
            showErrorAlert('Please do not exceed 140 characters for the title in row '  + (i+1));
            titleError = true;                                       
        }
    });
    
    if(titleError) {
        return false;
    }
    
    // Ensure there are no two-level gaps in the outline
    var gapTooBig = false;        
    titleFields  = $('.outlinerInput').each(function(i, obj){
        nextField = getNextTitleField(this);
        if (nextField) {
            if ($(nextField).data('level') - $(this).data('level') >= 2) {
                showErrorAlert('Cannot save: too large a gap between supporting points between rows ' + (i+1) + ' and ' + (i+2));  
                gapTooBig = true;                          
                return false;
            }
        }
    });
    
    return !gapTooBig;
}

function saveOutline() {
    if(validateInputs()) {    
        if (confirm('Going to save ' + titleFields.length + ' points.  Are you sure?')) {        
            saveMainPoint();            
        }       
    }
}

$(document).ready(function() {
    setOutlinerEvents();
    $("#saveOutline").on("click", saveOutline)
});
