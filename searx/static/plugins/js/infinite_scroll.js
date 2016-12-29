$(document).ready(function() {
    var win = $(window);
    win.scroll(function() {
        if ($(document).height() - win.height() == win.scrollTop()) {
            var formData = $('#pagination form:last').serialize();
            if (formData) {
                var pageno = $('#pagination input[name=pageno]:last').attr('value');
                $('#pagination').html('<div class="loading-spinner"></div>');
                $.post('./', formData, function (data) {
                    var lastImageHref = $('.result-images:last a').attr('href');
                    var body = $(data);
                    $('a[href^="#open-modal"]:last').attr('href', '#open-modal-1-' + pageno);
                    body.find('.modal-image a:first').attr('href', lastImageHref);
                    $('#pagination').remove();
                    $('#main_results').append('<hr/>');
                    $('#main_results').append(body.find('.result'));
                    $('#main_results').append(body.find('#pagination'));
                });
            }
        }
    });
});
