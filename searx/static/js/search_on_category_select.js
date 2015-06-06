$(document).ready(function() {
    if($('#q').length) {
        $('#categories label').click(function(e) {
            $('#categories input[type="checkbox"]').each(function(i, checkbox) {
                $(checkbox).prop('checked', false);
            });
            $('#categories label').removeClass('btn-primary').removeClass('active').addClass('btn-default');
            $(this).removeClass('btn-default').addClass('btn-primary').addClass('active');
            $($(this).children()[0]).prop('checked', 'checked');
            if($('#q').val()) {
                $('#search_form').submit();
            }
            return false;
        });
    }
});
