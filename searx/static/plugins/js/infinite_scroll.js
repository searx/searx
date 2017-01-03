$(document).ready(function() {
    var win = $(window);
    win.scroll(function() {
        if ($(document).height() - win.height() == win.scrollTop()) {
            var formData = $('#pagination form:last').serialize();
            if (formData) {
                $('#pagination').html('<div class="loading-spinner"></div>');
                $.post('./', formData, function (data) {
                    var body = $(data);
                    $('#pagination').remove();
                    $('#main_results').append('<hr/>');
                    $('#main_results').append(body.find('.result'));
                    $('#main_results').append(body.find('#pagination'));
                });
            }
        }
    });
});
