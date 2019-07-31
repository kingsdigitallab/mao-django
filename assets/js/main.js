$(function() {
    // Your JS Here
    $('#content1 a').click(function(event) {
        $('.name-active').removeClass('name-active'); 
        $target = $(event.currentTarget); 
        $target.addClass('name-active');
        if ($(window).width() < 960) {
            $("#page-content"). prop("checked", false);
         }
    });
});
