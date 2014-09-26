/**
 _                 _       _                  
| |__   ___   ___ | |_ ___| |_ _ __ __ ___  __
| '_ \ / _ \ / _ \| __/ __| __| '__/ _` \ \/ /
| |_) | (_) | (_) | |_\__ | |_| | | (_| |>  < 
|_.__/ \___/ \___/ \__|___/\__|_|  \__,_/_/\_\.js

*/

$(document).ready(function(){
    $('.btn-toggle .btn').click(function() {
        var btnClass = 'btn-' + $(this).data('btn-class');
        var btnLabelDefault = $(this).data('btn-label-default');
        var btnLabelToggled = $(this).data('btn-label-toggled');
        if(btnLabelToggled != '')
        {
            if($(this).hasClass('btn-default'))
            {
                
                var html = $(this).html().replace(btnLabelDefault, btnLabelToggled);
            }
            else
            {
                var html = $(this).html().replace(btnLabelToggled, btnLabelDefault);
            }
            $(this).html(html);
        }
        $(this).toggleClass(btnClass);
        $(this).toggleClass('btn-default');
    });
});
