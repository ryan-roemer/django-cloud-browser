/**
 * Cloud Browser basic navigation support.
 */

var CloudBrowser = {
    /** Submit the "next" page results form. */
    submitForm: function (formId) {
        document.getElementById(formId).submit();
        return false;
    },
    /** Return key pressed */
    enterPressed: function (event) {
        var key = window.event ?
            window.event.keyCode /*IE*/ :
            event.which /*FF*/;
        return key === 13;
    },
    /** Submit form on enter. */
    submitOnEnter: function (event, formId) {
        if (CloudBrowser.enterPressed(event)) {
            CloudBrowser.submitForm(formId);
        }
    }
};
