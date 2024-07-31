document.addEventListener('DOMContentLoaded', function() {
    function initSelect2(selector, url, placeholder) {
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
                        results: data
                    };
                },
                cache: true
            },
            minimumInputLength: 2,
            placeholder: placeholder,
            allowClear: true,
            tags: true
        });
    }

    // Inizializza Select2 per specie, località e monte
    initSelect2("#specie", "/api/specie/autocomplete", "Cerca o inserisci una specie");
    initSelect2("#codice-localita", "/api/localita/autocomplete", "Cerca o inserisci un codice località");
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
});