$(document).ready(function () {
    var Table = function (table) {
        var hrow = table.find('.result-table-header');
        if (hrow.length !== 1) {
            throw 'table must contain one header row';
        }
        this.headers = hrow.find('th');
        if (this.headers.length < 1) {
            throw 'table must contain at least one column';
        }
        this.columns = [];

        var headerClickHandler = function (colnum) {
            return function (e) {
                var $this = $(this);
                var desc = $this.data('order') === 'desc';

                tbl.headers
                    .find('span.glyphicon')
                    .removeClass('glyphicon-sort-by-attributes glyphicon-sort-by-attributes-alt')
                    .addClass('glyphicon-sort');

                tbl.headers.data('order', null);

                $this
                    .find('span.glyphicon')
                    .removeClass('glyphicon-sort')
                    .addClass('glyphicon-sort-by-attributes' + (desc ? '-alt' : ''));

                $this.data('order', desc ? 'asc' : 'desc');

                tbl.sort(colnum, !desc);
            };
        };

        for (var i = 0; i < this.headers.length; i++) {
            var header = $(this.headers[i]);
            var field = header.data('field');
            if (field.length === 0) {
                throw 'empty field in ' + (i + 1) + ' column';
            }
            if (header.hasClass('sortable')) {
                header.addClass('cursor-pointer');
                header.append('<span class="pull-right glyphicon glyphicon-sort" />');
                var tbl = this;
                header.on('click', headerClickHandler(i));
            }
            this.columns.push(field);
        }
        this.table = table;
        this.rows = [];
        this.hidden = 0;
    };

    Table.prototype.addRows = function (data, hidden) {
        if (data instanceof Array) {
            for (var i = 0; i < data.length; i++) {
                this.addRows(data[i], hidden);
            }
            return;
        }

        hidden = hidden === true;
        if (hidden) {
            this.hidden++;
        }

        var urlfield = this.table.data('field-url');
        if (!urlfield) {
            urlfield = 'url';
            console.warn('data-field-url not found in table, using default value');
        }
        var url = data[urlfield];
        if (!url) {
            throw 'URL field not found';
        }

        var cols = [];
        for (var j = 0; j < this.columns.length; j++) {
            var col = this.columns[j];
            if (typeof data[col] === 'undefined') {
                throw col + ' field not found';
            }
            cols.push(data[col].toString().trim());
        }

        this.rows.push({
            url:     url,
            hidden:  hidden,
            columns: cols
        });
    };

    Table.prototype.build = function () {
        if (this.rows.length === 0) {
            throw 'no rows were added';
        }

        this.table.find('tr').not('.result-table-header').remove();

        var html = '';

        for (var i = 0; i < this.rows.length; i++) {
            var row = this.rows[i];

            var css = 'clickable-tr';
            if (row.hidden) {
                css += ' hidden';
            }

            html += '<tr class="' + css + '" data-url="' + row.url + '">';
            for (var j = 0; j < row.columns.length; j++) {
                html += '<td>' + row.columns[j] + '</td>';
            }
            html += '</tr>';
        }

        if (this.hidden > 0) {
            var trid = 'show-all-' + this.table.data('index');

            html += '<tr class="clickable-tr show-all-tr" id="' + trid + '">';
            html += '<td colspan="' + this.columns.length + '">';
            html += '<span class="btn-link text-info">';
            html += 'Display other ' + this.hidden + ' results';
            html += '</span>';
            html += '</td>';
            html += '</tr>';

            this.table.append(html);

            var tbl = this;

            $('#' + trid).on('click', function (e) {
                $(this).remove();
                tbl.table.find('tr.hidden').removeClass('hidden');

                for (var j = 0; j < tbl.rows.length; j++) {
                    tbl.rows[j].hidden = false;
                }
                tbl.hidden = 0;
            });
        } else {
            this.table.append(html);
        }

        this.table.find('tr.clickable-tr[data-url]').on('click', function () {
            window.open($(this).data('url'), '_blank');
        });
    };

    Table.prototype.sort = function (colnum, asc) {
        if (colnum >= this.headers.length) {
            throw 'invalid column number';
        }
        this.rows.sort(function (a, b) {
            var x = a.columns[colnum];
            var y = b.columns[colnum];

            // always push empty strings to the end of the list
            if (!x && !y) {
                return 0;
            }
            if (!x) {
                return 1;
            }
            if (!y) {
                return -1;
            }
            var result = x.localeCompare(y, 'en', { numeric: true });
            if (asc) {
                return result;
            }
            return -result;
        });
        this.build();
        this.table
            .find('tr')
            .not('.result-table-header, .show-all-tr')
            .find('td:nth-child(' + (colnum + 1) + ')')
            .addClass('sort-highlight');
    };

    $('.video-download-link').on('click', function (event) {
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

        $.getJSON('/video_links', { url: url, h: hash }, function (data) {
            var table = new Table(result_table);

            if (data.preferred.length > 0) {
                table.addRows(data.preferred, false);

                if (data.filtered.length > 0) {
                    table.addRows(data.filtered, true);
                }

                table.build();

                loadicon.addClass('hidden');
                result_panel.removeClass('hidden');
            } else if (data.filtered.length > 0) {
                table.addRows(data.filtered, false);
                table.build();

                var msg = 'No results in preferred formats were found, but there ';
                if (data.filtered.length === 1) {
                    msg += 'is one result in the other format.';
                } else {
                    msg += 'are ' + data.filtered.length + ' results in other formats.';
                }

                var aid = 'show-filtered-' + index;
                var link = '<a id="' + aid + '" ' +
                    'class="cursor-pointer">Display all available results</a>.';

                loadicon.html(p(msg) + p(link));

                $('#' + aid).on('click', function (event) {
                    loadicon.addClass('hidden');
                    result_panel.removeClass('hidden');
                });
            } else {
                loadicon.html(p('No media available for download.'));
            }
        })
        .fail(function () {
            loadicon.html(p('Could not load data.'));
        });
    });
});

