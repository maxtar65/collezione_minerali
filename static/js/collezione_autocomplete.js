$(function() {
    function initAutocomplete(inputSelector, url) {
        $(inputSelector).autocomplete({
            source: function(request, response) {
                $.ajax({
                    url: url,
                    dataType: "json",
                    data: {
                        query: request.term
                    },
                    success: function(data) {
                        response(data.map(function(item) {
                            return {
                                label: item.name,
                                value: item.name
                            };
                        }));
                    }
                });
            },
            minLength: 2,
            select: function(event, ui) {
                $(this).val(ui.item.value);
                return false;
            }
        }).autocomplete("instance")._renderItem = function(ul, item) {
            return $("<li>")
                .append("<div>" + item.label + "</div>")
                .appendTo(ul);
        };
    }

    initAutocomplete("#specie-search", "/api/specie/autocomplete");
    initAutocomplete("#localita-search", "/api/localita/autocomplete");
});