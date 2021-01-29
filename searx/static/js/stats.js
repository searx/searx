$(document).ready(function () {
    var qp_chart = {}
    var ticks = stats.ticks_search_time.map(e => (e*10) % 2 === 0 ? e : '');

    $('#engine_times_detail_title').hide();
    $('#engine_times_detail').hide();

    function add_qp_chart(id, data) {
        if (qp_chart[id] != null) {
            qp_chart[id].destroy()
        }
        qp_chart[id] = $.jqplot(id, [data.values], {
            seriesDefaults: {
                renderer: $.jqplot.BarRenderer,
                rendererOptions: {
                    highlightMouseDown: true
                },
                pointLabels: { show: true }
            },
            axes: {
                xaxis: {
                    renderer: $.jqplot.CategoryAxisRenderer,
                    ticks: ticks,
                    label: data.labels.xaxis,
                    min: 0,
                },
                yaxis: {
                    labelRenderer: $.jqplot.CanvasAxisLabelRenderer,
                    label: data.labels.yaxis
                }
            }
        });
    }

    if (stats.time.engine.length > 0) {
        $.jqplot('engine_times', [stats.time.http, stats.time.nohttp], {
            stackSeries: true,
            seriesDefaults: {
                renderer: $.jqplot.BarRenderer,
                rendererOptions: {
                    barMargin: 5,
                    barDirection: 'horizontal',
                },
                pointLabels: { show: true }
            },
            series: [
                { label: stats.time.labels.serie_http },
                { label: stats.time.labels.serie_nohttp },
            ],
            axes: {
                xaxis: {
                    label: stats.time.labels.xaxis,
                    labelRenderer: $.jqplot.CanvasAxisLabelRenderer
                },
                yaxis: {
                    renderer: $.jqplot.CategoryAxisRenderer,
                    ticks: stats.time.engine
                }
            },
            legend: {
                show: true
            }
        });

        $('#engine_times').bind('jqplotDataClick',
            function (ev, seriesIndex, pointIndex, data) {
                engine = stats.time.engine[pointIndex];
                $('#engine_times_detail_title').text(engine);
                $('#engine_times_detail_title').show();
                $('#engine_times_detail').show();
                add_qp_chart('engine_times_detail', {
                    labels: {
                        'xaxis': stats.search_time.labels.xaxis,
                        'yaxis': stats.search_time.labels.yaxis
                    },
                    values: stats.time.detail[engine]
                });
            }
        )
    }

    if (stats.error.engines.length > 0) {
        $.jqplot('engine_errors', stats.error.data, {
            stackSeries: true,
            seriesDefaults: {
                renderer: $.jqplot.BarRenderer,
                rendererOptions: {
                    barMargin: 5,
                    barDirection: 'horizontal',
                },
                pointLabels: { show: true }
            },
            series: stats.error.labels.series.map(e=>{ return {"label": e} }),
            axes: {
                xaxis: {
                    label: stats.error.labels.xaxis,
                    labelRenderer: $.jqplot.CanvasAxisLabelRenderer,
                    max: 100
                },
                yaxis: {
                    renderer: $.jqplot.CategoryAxisRenderer,
                    ticks: stats.error.engines
                }
            },
            legend: {
                show: true,
            }
        });
    }

    $.jqplot('engine_scores', [stats.score.stat], {
        seriesDefaults: {
            renderer: $.jqplot.BubbleRenderer,
            rendererOptions: {
                bubbleAlpha: 0.0,
                highlightAlpha: 0.4
            },
            shadow: false
        },
        axes: {
            xaxis: {
                label: stats.score.labels.xaxis,
                labelRenderer: $.jqplot.CanvasAxisLabelRenderer,
                min: -5,
            },
            yaxis: {
                label: stats.score.labels.yaxis,
                labelRenderer: $.jqplot.CanvasAxisLabelRenderer,
                min: -10,
                pad: 1,
                showTicks: false
            }
        },
        cursor: {
            show: false,
            showTooltip: true
        }
    });

    add_qp_chart('search_time', stats.search_time);

});
