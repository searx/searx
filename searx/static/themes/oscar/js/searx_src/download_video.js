$(document).ready(function() {
    $('.video-download-link').on('click', video_download_handler);

    function video_download_handler(event) {
        function p(str) {
            return '<p class="text-muted">' + str + '</p>';
        }

        function tr(ar, url) {
            var result = '';
            for (var i = 0; i < ar.length; i++) {
                result += '<td>' + ar[i] + '</td>';
            }
            return '<tr class="clickable-tr" data-url="' + url + '">' +
                result + '</tr>';
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
                if (data.filtered < 1) {
                    $(loadicon).html(p('Nothing found.'));
                    return;
                }

                ctx.data('filter', 'nofilter');

                var link = '<a id="repeat-link-' + index + '" ' +
                           'class="cursor-pointer">' +
                           'Click here</a>';

                var msg = 'No results in preferred formats were found, but there ';
                if (data.filtered === 1) {
                    msg += 'is one result in other format.';
                } else {
                    msg += 'are ' + data.filtered + ' results in other formats.';
                }
                msg = p(msg) + p(link + ' to display all results.');

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
                    fmt.vc
                ], fmt.url);
            }
            $(result_table).append(html);
            $(result_table).find('tr.clickable-tr').click(function() {
                window.open($(this).data('url'), '_blank');
            });
            $(result_panel).removeClass('hidden');
            $(loadicon).addClass('hidden');
        })
        .fail(function() {
            $(loadicon).html(p('Could not load data.'));
        });
    }
});

