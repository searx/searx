$(document).ready(function() {
    $('.video-download-link').on('click', video_download_handler);

    function video_download_handler(event) {
        function p(str) {
            return '<p class="text-muted">' + str + '</p>';
        }

        function tr(ar) {
            var result = '';
            for (var i = 0; i < ar.length; i++) {
                result += '<td>' + ar[i] + '</td>';
            }
            return '<tr>' + result + '</tr>';
        }

        $(this).off(event);

        var ctx          = $(this);
        var url          = ctx.data('video-url');
        var hash         = ctx.data('hash');
        var result_table = ctx.data('result-table');
        var result_panel = ctx.data('result-panel');
        var loadicon     = ctx.data('load-icon');
        var filter       = ctx.data('filter');
        var index        = ctx.data('index');

        var options = {
            url:    url,
            h:      hash,
            filter: filter === 'filter'
        };

        $.getJSON('/video_links', options, function(data) {
            if (data.formats.length < 1) {
                var msg = p('Nothing found.');

                if (data.filtered < 1) {
                    $(loadicon).html(msg);
                    return;
                }

                ctx.data('filter', 'nofilter');

                var link = '<a id="repeat-link-' + index + '" ' +
                           'class="cursor-pointer">' +
                           'Click here</a>';

                msg += p(data.filtered + ' results were filtered out.');
                msg += p(link + ' to view results in all formats.');

                var defaultLoadIconHtml = $(loadicon).html();
                $(loadicon).html(msg);

                $('#repeat-link-' + index).on('click', function() {
                    $(this).off(event);
                    $(loadicon).html(defaultLoadIconHtml);
                    $.proxy(video_download_handler, ctx)();
                });

                return;
            }
            var html = '';
            for (var i = data.formats.length - 1; i >= 0; i--) {
                var fmt = data.formats[i];
                html += tr([
                    fmt.name,
                    fmt.note,
                    fmt.ext,
                    fmt.resolution,
                    fmt.ac,
                    fmt.vc,
                    '<a target="blank" href="' + fmt.url + '">link</a>'
                ]);
            }
            $(result_table).append(html);
            $(result_panel).removeClass('hidden');
            $(loadicon).addClass('hidden');
        })
        .fail(function() {
            $(loadicon).html(p('Could not load data.'));
        });
    }
});

