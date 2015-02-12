/* Javascript for StudioEditableXBlockMixin. */
function StudioEditableXBlockMixin(runtime, element) {
    "use strict";
    
    var fields = [];
    $(element).find('.field-data-control').each(function() {
        var $field = $(this);
        var $wrapper = $field.closest('li');
        var $resetButton = $wrapper.find('button.setting-clear');
        var cast = $wrapper.data('cast');
        fields.push({
            $field: $field,
            name: $wrapper.data('field-name'),
            isSet: function() { return $wrapper.hasClass('is-set'); },
            val: function() {
                var val = $field.val();
                // Cast values to the appropriate type so that we send nice clean JSON over the wire:
                if (cast == 'boolean')
                    return (val == 'true' || val == '1');
                if (cast == "integer")
                    return parseInt(val, 10);
                if (cast == "float")
                    return parseFloat(val);
                return val;
            }
        });
        $field.bind("change input paste", function() {
            // Field value has been modified:
            $wrapper.addClass('is-set');
            $resetButton.removeClass('inactive').addClass('active');
        });
        $resetButton.click(function() {
            $field.val($wrapper.data('default'));
            $wrapper.removeClass('is-set');
            $resetButton.removeClass('active').addClass('inactive');
        });
    });

    var studio_submit = function(data) {
        var handlerUrl = runtime.handlerUrl(element, 'submit_studio_edits');
        runtime.notify('save', {state: 'start', message: gettext("Saving")});
        $.ajax({
            type: "POST",
            url: handlerUrl,
            data: JSON.stringify(data),
            dataType: "json",
            global: false,  // Disable Studio's error handling that conflicts with studio's notify('save') and notify('cancel') :-/
            success: function(response) { runtime.notify('save', {state: 'end'}); }
        }).fail(function(jqXHR) {
            var message = gettext("This may be happening because of an error with our server or your internet connection. Try refreshing the page or making sure you are online.");
            if (jqXHR.responseText) { // Is there a more specific error message we can show?
                try {
                    message = JSON.parse(jqXHR.responseText).error;
                } catch (error) { message = jqXHR.responseText.substr(0, 300); }
            }
            runtime.notify('error', {title: gettext("Unable to update settings"), message: message});
        });
    };

    $('.save-button', element).bind('click', function(e) {
        e.preventDefault();
        var values = {};
        var notSet = []; // List of field names that should be set to default values
        for (var i in fields) {
            var field = fields[i];
            if (field.isSet()) {
                values[field.name] = field.val();
            } else {
                notSet.push(field.name);
            }
        }
        studio_submit({values: values, defaults: notSet});
    });

    $(element).find('.cancel-button').bind('click', function(e) {
        e.preventDefault();
        runtime.notify('cancel', {});
    });
}
