$(document).ready(function() {
    $('[name=assignmentEditButton]').toggle();
    $("[name=assignmentRow]").hover(function () {
       $(this).toggleClass("assignmentRowHover");
       $('[name=assignmentEditButton]', $(this)).toggle(); 
    });
});
