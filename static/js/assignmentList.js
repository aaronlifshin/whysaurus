
$(document).ready(function() {
    if(!isMobile()) {
        $('[name=assignmentEditButton]').toggle();
        $("[name=assignmentRow]").hover(function () {
           $(this).toggleClass("assignmentRowHover");
           $('[name=assignmentEditButton]', $(this)).toggle();            
        });
        
        $("[name=assignmentRow]").click(function() {
            window.location.href=$(this).find('[name=assignmentLink]').attr('href');
        });
    }
});
