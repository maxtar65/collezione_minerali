document.addEventListener('DOMContentLoaded', function() {
    function initSelect2(selector, url, placeholder, callback) {
        $(selector).select2({
            ajax: {
                url: url,
                dataType: 'json',
                delay: 250,
                data: function (params) {
                    return {
                        query: params.term
                    };
                },
                processResults: function (data) {
                    return {
                        results: data.map(function(item) {
                            return {
                                id: item.id,
                                text: item.name,
                                additionalData: item.additionalData
                            };
                        })
                    };
                },
                cache: true
            },
            minimumInputLength: 2,
            placeholder: placeholder,
            allowClear: true,
            tags: true
        }).on('select2:select', function (e) {
            if (callback) {
                callback(e.params.data);
            }
        });
    }

    // Inizializza Select2 per specie
    initSelect2("#specie", "/api/specie/autocomplete", "Cerca o inserisci una specie");

    // Inizializza Select2 per codice località con callback
    initSelect2("#codice-localita", "/api/localita/autocomplete", "Cerca o inserisci un codice località", function(selectedData) {
        if (selectedData.additionalData) {
            $('#loc-monte').val(selectedData.additionalData.loc_monte).trigger('change');
            // Popolamento di altri campi correlati alla località, se necessario
            // Esempio:
            // $('#campo-comune').val(selectedData.additionalData.comune);
            // $('#campo-provincia').val(selectedData.additionalData.provincia);
        }
    });

    // Inizializza Select2 per monte
    initSelect2("#loc-monte", "/api/localita/monte_autocomplete", "Cerca o inserisci un monte");

    // Inizializza Select2 per luogo acquisizione con possibilità di aggiungere nuovi tag
    $('#luogo-acq').select2({
        tags: true,
        tokenSeparators: [',', ' '],
        ajax: {
            url: '/api/luoghi_acquisizione',
            dataType: 'json',
            processResults: function (data) {
                console.log("Select2 data:", data);
                return {
                    results: data.map(function(item) {
                        return { id: item, text: item };
                    })
                };
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.error("Error fetching select2 data:", textStatus, errorThrown);
            }
        },
        placeholder: 'Seleziona o inserisci un luogo',
        allowClear: true
    });

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

    // Gestione del form di ricerca
    $('#searchForm').submit(function(e) {
        e.preventDefault();
        var specieSearch = $('#specie-search').val();
        var localitaSearch = $('#localita-search').val();
        var codiceSearch = $('#codice-search').val();
        
        var url = '/collezione?';
        if (specieSearch) url += 'specie-search=' + encodeURIComponent(specieSearch) + '&';
        if (localitaSearch) url += 'localita-search=' + encodeURIComponent(localitaSearch) + '&';
        if (codiceSearch) url += 'codice-search=' + encodeURIComponent(codiceSearch);
        
        window.location.href = url;
    });

    // Gestione della paginazione
    $('.pagination-link').click(function(e) {
        e.preventDefault();
        var page = $(this).data('page');
        var currentUrl = new URL(window.location.href);
        currentUrl.searchParams.set('page', page);
        window.location.href = currentUrl.toString();
    });

    // Gestione dell'interazione tra specie e specie non valida
    $('#specie').on('change', function() {
        if ($(this).val()) {
            $('#specie_non_valida').val('').prop('disabled', true);
        } else {
            $('#specie_non_valida').prop('disabled', false);
        }
    });

    $('#specie_non_valida').on('input', function() {
        if ($(this).val()) {
            $('#specie').val(null).trigger('change').prop('disabled', true);
        } else {
            $('#specie').prop('disabled', false);
        }
    });
});