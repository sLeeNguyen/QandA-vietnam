/* 

JS Table Of Content 
======================
1. Scroll to Top
2. Team member flip


*/

function clickScroll() {
    var bodyTop = $("html, body");
    bodyTop.animate({
        scrollTop: 0
    }, 800, "easeOutCubic");
}

$(function () {
    /*=============================================
        	1. Scroll to Top
    ===============================================*/

    function scrolltop() {
        var wind = $(window);
        wind.on("scroll", function () {
            var scrollTop = $(window).scrollTop();
            if (scrollTop >= 500) {
                $(".scroll-top").fadeIn("slow");

            } else {
                $(".scroll-top").fadeOut("slow");
            }
        });
    }
    scrolltop();

    /*=============================================
        	2. Team member flip
    ===============================================*/

    $(".team-member-wrapper.owl-carousel").owlCarousel({
        autoplay: true,
        loop: true,
        responsive: {
            0: {
                items: 1
            },
            480: {
                items: 2
            },
            678: {
                items: 3
            },
        }
    });


    RTE_DefaultConfig.url_base = 'richtexteditor'
    var editor1cfg = {}
    editor1cfg.toolbar = "basic";
    var editor1 = new RichTextEditor("#div_editor1", editor1cfg);
});