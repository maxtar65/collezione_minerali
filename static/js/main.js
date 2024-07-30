document.addEventListener('DOMContentLoaded', function() {
    // Funzione per inizializzare l'autocomplete
    function initAutocomplete(inputSelector, url) {
        $(inputSelector).autocomplete({
            hint: false,
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

    // Inizializza l'autocompletamento per specie e località
    initAutocomplete('#specie-search', '/api/specie/autocomplete');
    initAutocomplete('#localita-search', '/api/localita/autocomplete');

    // Gestione della doppia conferma per l'eliminazione
    $('input[id^="confirmDelete"]').change(function() {
        var id = this.id.replace('confirmDelete', '');
        $('#deleteButton' + id).prop('disabled', !this.checked);
    });

    // Resetta lo stato del checkbox e del pulsante quando il modal viene aperto
    $('.modal').on('show.bs.modal', function () {
        var id = this.id.replace('deleteModal', '');
        $('#confirmDelete' + id).prop('checked', false);
        $('#deleteButton' + id).prop('disabled', true);
    });

    // Inizializzazione di Select2 per i form di collezione
    function initSelect2(selector, url, placeholder) {
        $(selector).select2({
            ajax: {
                url: url,
                dataType: 'json',
                delay: 250,
                processResults: function (data) {
                    return {
                        results: $.map(data, function(item) {
                            return {
                                text: item.name,
                                id: item.id
                            }
                        })
                    };
                },
                cache: true
            },
            minimumInputLength: 2,
            placeholder: placeholder
        });
    }

    // Inizializza Select2 per specie e località nei form
    initSelect2('#specie-select', '/api/specie', 'Seleziona una specie');
    initSelect2('#localita-select', '/api/localita', 'Seleziona una località');
});