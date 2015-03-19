$(document).ready(function() {
    $('#addAnotherDocument').click(function() {
        var lastExistingDocument = $('[name="documentControls"]').last();
        var newDocumentRow = lastExistingDocument.clone();
        var rowNumber = $(lastExistingDocument).data('documentnumber') + 1;
        $('[name="documentNumber"]', newDocumentRow).text(rowNumber.toString());
        lastExistingDocument.after(newDocumentRow); 
        $(newDocumentRow).data('documentnumber', rowNumber);
        
    });
});
