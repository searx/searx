$(document).ready(function() {
    function tr(ar, url, hidden) {
        var result = '';
        for (var i = 0; i < ar.length; i++) {
            result += '<td>' + ar[i] + '</td>';
        }
        var css = 'clickable-tr';
        if (hidden === true) {
            css += ' hidden';
        }
        return '<tr class="' + css + '" data-url="' + url + '">' + result + '</tr>';
    }

    function displayResults(table, data, hidden) {
        var html = '';
        for (var i = data.length - 1; i >= 0; i--) {
            var fmt = data[i];
            html += tr([
                    fmt.name,
                    fmt.note,
                    fmt.ext,
                    fmt.resolution,
                    fmt.ac,
                    fmt.vc
            ], fmt.url, hidden);
        }
        table.append(html);
    }

    $('.video-download-link').on('click', function(event) {
        function p(str) {
            return '<p class="text-muted">' + str + '</p>';
        }

        $(this).off(event);

        var ctx          = $(this);
        var url          = ctx.data('video-url');
        var hash         = ctx.data('hash');
        var index        = ctx.data('index');

        var result_table = $(ctx.data('result-table'));
        var result_panel = $(ctx.data('result-panel'));
        var loadicon     = $(ctx.data('load-icon'));

        $.getJSON('/video_links', { url: url, h: hash }, function(data) {
            if (data.preferred.length > 0) {
                displayResults(result_table, data.preferred, false);

                if (data.filtered.length > 0) {
                    var trid = 'show-all-' + index;
                    var st = '<tr class="clickable-tr" id="' + trid + '">' +
                        '<td colspan="6">Click here to display other ' +
                        data.filtered.length + ' results.</td></tr>';

                    result_table.append(st);

                    displayResults(result_table, data.filtered, true);

                    $('#' + trid).on('click', function(event) {
                        result_table.find('tr.hidden').removeClass('hidden');
                        $(this).addClass('hidden');
                    });
                }

                loadicon.addClass('hidden');
                result_panel.removeClass('hidden');
            } else if (data.filtered.length > 0) {
                displayResults(result_table, data.filtered, false);

                var msg = 'No results in preferred formats were found, but there ';
                if (data.filtered.length === 1) {
                    msg += 'is one result in the other format.';
                } else {
                    msg += 'are ' + data.filtered.length + ' results in other formats.';
                }
            
                var aid = 'show-filtered-' + index;
                var link = '<a id="' + aid + '" class="cursor-pointer">Click here</a> ' + 
                    'to display all results.';

                loadicon.html(p(msg) + p(link));

                $('#' + aid).on('click', function(event) {
                    loadicon.addClass('hidden');
                    result_panel.removeClass('hidden');
                });
            } else {
                loadicon.html(p('Nothing found.'));
            }

            result_table.find('tr.clickable-tr[data-url]').click(function() {
                window.open($(this).data('url'), '_blank');
            });
        })
        .fail(function() {
            loadicon.html(p('Could not load data.'));
        });
    });
});

