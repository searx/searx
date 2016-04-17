$(document).ready(function() {
    $('.video-download-link').on('click', function(event) {
        var url = $(this).data('video-url');
        var hash = $(this).data('hash');
        var result_table = $(this).data('result-table');
        var loadicon = $(this).data('load-icon');

        // table header
        var html =
            '<tr>' +
                '<th>format</th>' +
                '<th>comment</th>' +
                '<th>extension</th>' +
                '<th>resolution</th>' +
                '<th>audio</th>' +
                '<th>video</th>' +
                '<th>download</th>' +
            '</tr>';

        $.getJSON('/video_links', { url: url, h: hash }, function(data) {
            if (data.formats.length < 1) {
                $(loadicon).html('<p class="text-muted">nothing found</p>');
                return;
            }
            for (var i = data.formats.length - 1; i >= 0; i--) {
                var fmt = data.formats[i];
                var row = '';
                row += '<td>' + fmt.name + '</td>';
                row += '<td>' + fmt.note + '</td>';
                row += '<td>' + fmt.ext + '</td>';
                row += '<td>' + fmt.resolution + '</td>';
                row += '<td>' + fmt.ac + '</td>';
                row += '<td>' + fmt.vc + '</td>';
                row += '<td><a href="' + fmt.url + '">link</a></td>';
                html += '<tr>' + row + '</tr>';
            }
            $(result_table).html(html);
            $(result_table).removeClass('hidden');
            $(loadicon).addClass('hidden');
        })
        .fail(function() {
            $(loadicon).html('<p class="text-muted">could not load data</p>');
        });

        // this event handler should only be executed once
        $(this).off(event);    
    });
});

