/**
 * Cloud Browser admin navigation support.
 *
 * Note: Requires jQuery, but we use the Django Admin version, which can be
 * relied on to exist.
 */
var CloudBrowserAdmin = {
    /**
     * Return whether container div is closed (from URL GET params).
     *
     * Note that URL param: "closed=1" is closed and all else is open.
     */
    containerIsClosed: function () {
        var currentUrl = window.location.href;
        var queryObj = CloudBrowser.getQueryObj(currentUrl);
        return queryObj.params.closed === '1';
    },

    /**
     * Set state on all links.
     *
     * @param $allLinks: Links to patch HREF parameter.
     * @param $allForms: Forms to patch ACTION parameter.
     * @param closed: (Optional) Set to 'closed' state?
     */
    setLinkState: function ($allLinks, $allForms, closed) {
        var $ = django.jQuery;

        // Get current closed state (if unset current state of window).
        closed = typeof closed === 'boolean' ?
            closed :
            CloudBrowserAdmin.containerIsClosed();

        var patchQuery = function (query) {
            var queryObj = CloudBrowser.getQueryObj(query);
            queryObj.params.closed = closed ? '1' : '0';
            return CloudBrowser.toQueryString(queryObj);
        };

        $allLinks.each(function (index, element) {
            var $element = $(element);
            $element.attr('href', patchQuery($element.attr('href')));
        });

        $allForms.each(function (index, element) {
            var $element = $(element);
            $element.attr('action', patchQuery($element.attr('action')));
        });
    },

    /**
     * Add all hider elements to page.
     */
    addHider: function ($all, $conts, $objs, closed, hiderCallback) {
        var $ = django.jQuery;
        closed = typeof closed === 'boolean' ?
            closed :
            CloudBrowserAdmin.containerIsClosed();
        hiderCallback = hiderCallback || function () {};

        // Add show/hide "hider" element.
        var hiderOpen = "&laquo;";
        var hiderClosed = "&raquo;";
        var $hiderOuter = $('<div />').
            attr('id', "cloud-browser-containers-hider-outer").
            prependTo($conts);
        var $hiderFull = $('<div />').
            addClass("cloud-browser-containers-hider").
            html(hiderOpen).
            prependTo($hiderOuter);

        // Add hidden "minimized" element.
        var $hiderMin = $hiderFull.
            clone().
            removeClass("cloud-browser-containers-hider").
            addClass("cloud-browser-containers-hider-min").
            html(hiderClosed);
        var $min = $('<div />').
            attr('id', "cloud-browser-containers-min").
            hide().
            append($hiderMin).
            prependTo($all);

        var objsOpenMargin = $objs.css('marginLeft');
        var objsClosedMargin = -2;

        // Initial setup.
        if (closed) {
            $conts.hide();
            $min.show();
            $objs.css('marginLeft', objsClosedMargin);
            hiderCallback(true /* closed */);
        }

        var closeFn = function () {
            // Currently open. Close.
            $conts.fadeOut('fast', function () {
                $min.fadeIn('fast');
                $objs.css('marginLeft', objsClosedMargin);
                hiderCallback(true /* closed */);
            });
        };

        var openFn = function () {
            // Currently closed. Open.
            $min.fadeOut('fast', function () {
                $conts.fadeIn('fast');
                $objs.css('marginLeft', objsOpenMargin);
                hiderCallback(false /* opened */);
            });
        };
        
        // Toggle Functions.
        $hiderFull.click(closeFn);
        $hiderMin.click(openFn);
    }
};

