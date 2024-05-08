$(document).ready(function () {
    // highlight the clicked sidebar link on the object biography page 
    $('#content1 a').click(function(event) {
        $('.name-active').removeClass('name-active'); 
        $target = $(event.currentTarget); 
        $target.addClass('name-active');
        if ($(window).width() < 960) {
            $("#page-content"). prop("checked", false);
         }
    });
    var val;
    // aggregated map - expand and scroll down to the dropdown with the location description
    $(".leaflet-marker-icon").on('click', function(el) {
        $("input[type='checkbox']").prop('checked', false);
        if (val == undefined) {
            val = "map-tab-1";
        }
        $("#"+el.target.title).prev("input[type='checkbox']").prop('checked', true);
        $(".accordion-wrapper").animate({scrollTop: $("#"+el.target.title).parent(".accordion").offset().top-$("#map-tab-1").parent(".accordion").offset().top-$("#"+val).parent(".accordion").height()+42});
        val = el.target.title;
    })
});
