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

        var tbl = this;

        var sortBtnClickHandler = function (colnum) {
            return function (e) {
                var $this = $(this);
                var desc = $this.data('order') === 'desc';

                tbl.headers
                    .find('span.sort-btn')
                    .removeClass('glyphicon-sort-by-attributes glyphicon-sort-by-attributes-alt')
                    .addClass('glyphicon-sort')
                    .data('order', null);

                $this
                    .removeClass('glyphicon-sort')
                    .addClass('glyphicon-sort-by-attributes' + (desc ? '-alt' : ''))
                    .data('order', desc ? 'asc' : 'desc');

                tbl.sort(colnum, !desc);
            };
        };

        var filterBtnClickHandler = function (colnum) {
            return function (e) {
                var r = tbl.el.searchRow;
                var i = tbl.el.searchInput;

                tbl.headers.removeClass('tbl-highlight');

                if (r.hasClass('hidden') || i.data('colnum') === colnum) {
                    r.toggleClass('hidden');
                }

                i.val('').data('colnum', colnum);
                filterData(i);

                if (!r.hasClass('hidden')) {
                    var header = $(tbl.headers[colnum]);
                    header.addClass('tbl-highlight');
                    i.attr('placeholder', 'search (' + header.text() + ')');
                    i.focus();
                }
            };
        };

        var filterData = function (inp) {
            var num = inp.data('colnum');
            if (!tbl.validColNum(num)) {
                throw 'incorrect column number';
            }

            var str = inp.val().toLowerCase();

            for (var i = 0; i < tbl.rows.length; i++) {
                var row = tbl.rows[i];

                if (!(row._icolumns instanceof Array)) {
                    row._icolumns = [];
                }
                if (typeof row._icolumns[num] === 'undefined') {
                    row._icolumns[num] = row.columns[num].toLowerCase();
                }

                row.filtered = row._icolumns[num].indexOf(str) < 0;
            }

            tbl.build();
        };

        var searchInputChanged = function (e) {
            filterData($(e.target));
        };

        var iconCss = ' pull-right th-icon cursor-pointer glyphicon ';

        for (var i = 0; i < this.headers.length; i++) {
            var header = $(this.headers[i]);
            var field = header.data('field');
            if (field.length === 0) {
                throw 'empty field in ' + (i + 1) + ' column';
            }
            this.columns.push(field);

            // add sort button if needed
            if (header.hasClass('sortable')) {
                $('<span class="' + iconCss + 'sort-btn glyphicon-sort" />')
                    .on('click', sortBtnClickHandler(i))
                    .appendTo(header);
            }

            // add filter button
            $('<span class="' + iconCss + 'filter-btn glyphicon-search" />')
                .on('click', filterBtnClickHandler(i))
                .appendTo(header);
        }

        // add search row
        var srHtml = '';
        srHtml += '<tr class="result-search-row hidden">';
        srHtml += '<td colspan="' + this.columns.length + '">';
        srHtml += '<input type="text" placeholder="search" />';
        srHtml += '</td>';
        srHtml += '</tr>';

        this.el = {
            searchRow: $(srHtml)
        };
        table.append(this.el.searchRow);

        this.el.searchInput = this.el.searchRow
            .find('input')
            .css('width', '100%')
            .on('input', searchInputChanged);

        this.table = table;
        this.rows = [];
    };

    Table.prototype.validColNum = function (colnum) {
        return typeof colnum === 'number' && colnum >= 0 && colnum < this.columns.length;
    };

    Table.prototype.addRows = function (data, hidden) {
        if (data instanceof Array) {
            for (var i = 0; i < data.length; i++) {
                this.addRows(data[i], hidden);
            }
            return;
        }

        hidden = hidden === true;

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

        this.table.find('tr.data-row, tr.show-all-tr').remove();

        var html = '';

        for (var i = 0; i < this.rows.length; i++) {
            var row = this.rows[i];

            var css = 'clickable-tr data-row';
            if (row.hidden) {
                css += ' hidden';
            }
            if (row.filtered) {
                css += ' filtered';
            }

            html += '<tr class="' + css + '" data-url="' + row.url + '">';
            for (var j = 0; j < row.columns.length; j++) {
                html += '<td>' + row.columns[j] + '</td>';
            }
            html += '</tr>';
        }

        this.table.append(html);

        var notShown = this.table.find('tr.data-row.hidden').not('.filtered');

        if (notShown.length > 0) {
            var trid = 'show-all-' + this.table.data('index');

            html = '';
            html += '<tr class="clickable-tr show-all-tr" id="' + trid + '">';
            html += '<td colspan="' + this.columns.length + '">';
            html += '<span class="btn-link text-info">';
            html += 'Display other ' + notShown.length + ' results';
            html += '</span>';
            html += '</td>';
            html += '</tr>';

            this.table.append(html);

            var tbl = this;

            $('#' + trid).on('click', function (e) {
                $(this).remove();
                tbl.table.find('tr.data-row.hidden').removeClass('hidden');

                for (var j = 0; j < tbl.rows.length; j++) {
                    tbl.rows[j].hidden = false;
                }
            });
        }

        this.table.find('tr.data-row[data-url]').on('click', function () {
            window.open($(this).data('url'), '_blank');
        });

        var sortCol = this.table.data('sort-colnum');
        if (this.validColNum(sortCol)) {
            this.table
                .find('tr.data-row')
                .find('td:nth-child(' + (sortCol + 1) + ')')
                .addClass('tbl-highlight');
        }
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
        this.table.data('sort-colnum', colnum);
        this.build();
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

