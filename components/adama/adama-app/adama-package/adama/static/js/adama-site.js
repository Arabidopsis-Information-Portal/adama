ADAMA = '/adama';

function addNamespace(ns) {
    $('#namespaces').append(
        $('<li class="services">').append(
            $('<span>').text(ns.name)));
};

function refreshServices() {
    $.ajax({
        type: 'GET',
        url: ADAMA + '/namespaces',
        success: function(data) {
            console.log(data);
            $('#namespaces').empty();
            data.result.map(function(i) {
                addNamespace(i);
            });
            var now = new Date();
            $('#refreshedServices').timeago('update', now.toISOString());
        }
    });
};

$(document).ready(function () {
    $('#refreshedServices').timeago();
    $('#refreshServices').click(refreshServices);
    refreshServices();

    $('#namespaces').collapsibleList('.services', {search: true});
});
