function refreshServices() {
    $.ajax({
        type: 'GET',
        url: '/register',
        success: function(data) {
            console.log(data);
            $('#services').empty();
            data.adapters.map(function(i) {
                $('#services').append("---\n");
                $('#services').append(JSON.stringify(i, undefined, 2));
            });
        }
    });
};

$('#refreshServices').click(refreshServices);

refreshServices();
