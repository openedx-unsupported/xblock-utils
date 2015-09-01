function StudioContainerXBlockWithNestedXBlocksMixin(runtime, element) {
    var $buttons = $(".add-xblock-component-button", element),
        $element = $(element);

    function isSingleInstance($button) {
        return $button.data('single-instance');
    }

    $buttons.click(function(ev) {
        var $this = $(this);
        if ($this.is('.disabled')) {
            ev.preventDefault();
            ev.stopPropagation();
        } else {
            if (isSingleInstance($this)) {
                $this.addClass('disabled');
                $this.attr('disabled', 'disabled');
            }
        }
    });

    function updateButtons() {
        var nestedBlockLocations = $.map($element.find(".studio-xblock-wrapper"), function(block_wrapper) {
           return $(block_wrapper).data('locator');
        });

        $buttons.each(function() {
            var $this = $(this);
            if (!isSingleInstance($this)) {
                return;
            }
            var category = $this.data('category');
            var childExists = false;

            // FIXME: This is potentially buggy - if some XBlock's category is a substring of some other XBlock category
            // it will exhibit wrong behavior. However, it's not possible to do anything about that unless studio runtime
            // announces which block was deleted, not it's parent.
            for (var i = 0; i < nestedBlockLocations.length; i++) {
                if (nestedBlockLocations[i].indexOf(category) > -1) {
                    childExists = true;
                    break;
                }
            }

            if (childExists) {
                $this.attr('disabled', 'disabled');
                $this.addClass('disabled')
            }
            else {
                $this.removeAttr('disabled');
                $this.removeClass('disabled');
            }
        });
    }

    updateButtons();
    runtime.listenTo('deleted-child', updateButtons);
}
