ADAMA = '/adama';

function refreshServices() {
    $.ajax({
        type: 'GET',
        url: ADAMA + '/namespaces',
        success: function(data) {
            console.log(data);
            $('#services').empty();
            data.result.map(function(i) {
                $('#services').append("---\n");
                $('#services').append(JSON.stringify(i, undefined, 2));
                $('#services').append("\n");
            });
            var now = new Date();
            $('#refreshedServices').attr('title', now.toISOString());
            $('#refreshedServices').timeago();
        }
    });
};

$(document).ready(function () {
    $('#refreshServices').click(refreshServices);
    refreshServices();

    $('#my-list').collapsibleList('.header', {search: true});
});
