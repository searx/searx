$(document).ready(function() {
    if($('#q').length) {
        $('#categories label').click(function(e) {
            $('#categories input[type="checkbox"]').each(function(i, checkbox) {
                $(checkbox).prop('checked', false);
            });
            $(document.getElementById($(this).attr("for"))).prop('checked', true);
            if($('#q').val()) {
                $('#search_form').submit();
            }
            return false;
        });
        $('#time-range > option').click(function(e) {
            if($('#q').val()) {
                $('#search_form').submit();
            }
        });
        $('#language').change(function(e) {
            if($('#q').val()) {
                $('#search_form').submit();
            }
        });
    }
});
