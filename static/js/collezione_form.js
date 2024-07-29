document.addEventListener('DOMContentLoaded', function() {
    $('#specie-select').select2({
        ajax: {
            url: '/api/specie',
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
        placeholder: 'Seleziona una specie'
    });

    $('#localita-select').select2({
        ajax: {
            url: '/api/localita',
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
        placeholder: 'Seleziona una località'
    });
});