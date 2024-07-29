document.addEventListener('DOMContentLoaded', function() {
    function initAutocomplete(inputSelector, url) {
        $(inputSelector).autocomplete({
            hint: false,
            source: function(query, cb) {
                $.ajax({
                    url: url,
                    data: { query: query }
                }).then(function(res) {
                    cb(res);
                });
            },
            displayKey: 'name',
            templates: {
                suggestion: function(suggestion) {
                    return '<div>' + suggestion.name + '</div>';
                }
            }
        }).on('autocomplete:selected', function(event, suggestion, dataset) {
            $(this).val(suggestion.name);
        });
    }

    // Inizializza l'autocompletamento per specie e località
    initAutocomplete('#specie-search', '/api/specie');
    initAutocomplete('#localita-search', '/api/localita');

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
});
