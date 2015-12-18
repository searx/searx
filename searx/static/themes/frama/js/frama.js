if (document.getElementById('search_submit') !== null) {
    document.getElementById('search_submit').onclick = function() {
        if (document.getElementById('q') !== null && document.getElementById('q').value !== '' ) {
            document.getElementById('search_form').submit();
        }
    }
}
if (document.getElementById('search_empty') !== null) {
    document.getElementById('search_empty').onclick = function(event) {
        document.getElementById('q').value = '';
        document.getElementById('q').focus();
    }
}
