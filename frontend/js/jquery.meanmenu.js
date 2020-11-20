! function (e) {
    "use strict";
    e.fn.meanmenu = function (n) {
        var a = {
            meanMenuTarget: jQuery(this),
            meanMenuContainer: "body",
            meanMenuClose: "X",
            meanMenuCloseSize: "18px",
            meanMenuOpen: "<span /><span /><span />",
            meanRevealPosition: "right",
            meanRevealPositionDistance: "0",
            meanRevealColour: "",
            meanScreenWidth: "767",
            meanNavPush: "",
            meanShowChildren: !0,
            meanExpandableChildren: !0,
            meanExpand: "+",
            meanContract: "-",
            meanRemoveAttrs: !1,
            onePage: !1,
            meanDisplay: "block",
            removeElements: ""
        };
        n = e.extend(a, n);
        var t = window.innerWidth || document.documentElement.clientWidth;
        return this.each(function () {
            var e = n.meanMenuTarget,
                a = n.meanMenuContainer,
                r = n.meanMenuClose,
                i = n.meanMenuCloseSize,
                u = n.meanMenuOpen,
                m = n.meanRevealPosition,
                s = n.meanRevealPositionDistance,
                l = n.meanRevealColour,
                o = n.meanScreenWidth,
                c = n.meanNavPush,
                v = n.meanShowChildren,
                h = n.meanExpandableChildren,
                d = n.meanExpand,
                y = n.meanContract,
                j = n.meanRemoveAttrs,
                Q = n.onePage,
                f = n.meanDisplay,
                g = n.removeElements,
                p = !1;
            (navigator.userAgent.match(/iPhone/i) || navigator.userAgent.match(/iPod/i) || navigator.userAgent.match(/iPad/i) || navigator.userAgent.match(/Android/i) || navigator.userAgent.match(/Blackberry/i) || navigator.userAgent.match(/Windows Phone/i)) && (p = !0), (navigator.userAgent.match(/MSIE 8/i) || navigator.userAgent.match(/MSIE 7/i)) && jQuery("html").css("overflow-y", "scroll");
            var C = "",
                w = function () {
                    if ("center" === m) {
                        var e = (window.innerWidth || document.documentElement.clientWidth) / 2 - 22 + "px";
                        C = "left:" + e + ";right:auto;", p ? jQuery(".meanmenu-reveal").animate({
                            left: e
                        }) : jQuery(".meanmenu-reveal").css("left", e)
                    }
                },
                x = !1,
                A = !1;
            "right" === m && (C = "right:" + s + ";left:auto;"), "left" === m && (C = "left:" + s + ";right:auto;"), w();
            var E = "",
                M = function () {
                    jQuery(E).is(".meanmenu-reveal.meanclose") ? E.html(r) : E.html(u)
                },
                P = function () {
                    jQuery(".mean-bar,.mean-push").remove(), jQuery(a).removeClass("mean-container"), jQuery(e).css("display", f), x = !1, A = !1, jQuery(g).removeClass("mean-remove")
                },
                W = function () {
                    var n = "background:" + l + ";color:" + l + ";" + C;
                    if (t <= o) {
                        jQuery(g).addClass("mean-remove"), A = !0, jQuery(a).addClass("mean-container"), jQuery(".mean-container").prepend('<div class="mean-bar"><a href="#nav" class="meanmenu-reveal" style="' + n + '">Show Navigation</a><nav class="mean-nav"></nav></div>');
                        var r = jQuery(e).html();
                        jQuery(".mean-nav").html(r), j && jQuery("nav.mean-nav ul, nav.mean-nav ul *").each(function () {
                            jQuery(this).is(".mean-remove") ? jQuery(this).attr("class", "mean-remove") : jQuery(this).removeAttr("class"), jQuery(this).removeAttr("id")
                        }), jQuery(e).before('<div class="mean-push" />'), jQuery(".mean-push").css("margin-top", c), jQuery(e).hide(), jQuery(".meanmenu-reveal").show(), jQuery(".meanmenu-reveal").html(u), E = jQuery(".meanmenu-reveal"), jQuery(".mean-nav ul").hide(), v ? h ? (jQuery(".mean-nav ul ul").each(function () {
                            jQuery(this).children().length && jQuery(this, "li:first").parent().append('<a class="mean-expand" href="#" style="font-size: ' + i + '">' + d + "</a>")
                        }), jQuery(".mean-expand").on("click", function (e) {
                            e.preventDefault(), jQuery(this).hasClass("mean-clicked") ? (jQuery(this).text(d), jQuery(this).prev("ul").slideUp(300, function () {})) : (jQuery(this).text(y), jQuery(this).prev("ul").slideDown(300, function () {})), jQuery(this).toggleClass("mean-clicked")
                        })) : jQuery(".mean-nav ul ul").show() : jQuery(".mean-nav ul ul").hide(), jQuery(".mean-nav ul li").last().addClass("mean-last"), E.removeClass("meanclose"), jQuery(E).click(function (e) {
                            e.preventDefault(), !1 === x ? (E.css("text-align", "center"), E.css("text-indent", "0"), E.css("font-size", i), jQuery(".mean-nav ul:first").slideDown(), x = !0) : (jQuery(".mean-nav ul:first").slideUp(), x = !1), E.toggleClass("meanclose"), M(), jQuery(g).addClass("mean-remove")
                        }), Q && jQuery(".mean-nav ul > li > a:first-child").on("click", function () {
                            jQuery(".mean-nav ul:first").slideUp(), x = !1, jQuery(E).toggleClass("meanclose").html(u)
                        })
                    } else P()
                };
            p || jQuery(window).resize(function () {
                t = window.innerWidth || document.documentElement.clientWidth, P(), t <= o ? (W(), w()) : P()
            }), jQuery(window).resize(function () {
                t = window.innerWidth || document.documentElement.clientWidth, p ? (w(), t <= o ? !1 === A && W() : P()) : (P(), t <= o && (W(), w()))
            }), W()
        })
    }
}(jQuery);