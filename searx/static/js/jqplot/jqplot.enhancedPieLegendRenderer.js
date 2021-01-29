/**
 * jqPlot
 * Pure JavaScript plotting plugin using jQuery
 *
 * Version: 1.0.9
 * Revision: d96a669
 *
 * Copyright (c) 2009-2016 Chris Leonello
 * jqPlot is currently available for use in all personal or commercial projects 
 * under both the MIT (http://www.opensource.org/licenses/mit-license.php) and GPL 
 * version 2.0 (http://www.gnu.org/licenses/gpl-2.0.html) licenses. This means that you can 
 * choose the license that best suits your project and use it accordingly. 
 *
 * Although not required, the author would appreciate an email letting him 
 * know of any substantial use of jqPlot.  You can reach the author at: 
 * chris at jqplot dot com or see http://www.jqplot.com/info.php .
 *
 * If you are feeling kind and generous, consider supporting the project by
 * making a donation at: http://www.jqplot.com/donate.php .
 *
 * sprintf functions contained in jqplot.sprintf.js by Ash Searle:
 *
 *     version 2007.04.27
 *     author Ash Searle
 *     http://hexmen.com/blog/2007/03/printf-sprintf/
 *     http://hexmen.com/js/sprintf.js
 *     The author (Ash Searle) has placed this code in the public domain:
 *     "This code is unrestricted: you are free to use it however you like."
 * 
 */
(function($) {
    // class $.jqplot.EnhancedPieLegendRenderer
    // Legend renderer which can specify the number of rows and/or columns in the legend
    // Similar to EnhancedLegendRenderer, but for pie charts
    $.jqplot.EnhancedPieLegendRenderer = function(){
        $.jqplot.TableLegendRenderer.call(this);
    };
    
    $.jqplot.EnhancedPieLegendRenderer.prototype = new $.jqplot.TableLegendRenderer();
    $.jqplot.EnhancedPieLegendRenderer.prototype.constructor = $.jqplot.EnhancedPieLegendRenderer;
    
    // called with scope of legend.
    $.jqplot.EnhancedPieLegendRenderer.prototype.init = function(options) {
        // prop: numberRows
        // Maximum number of rows in the legend.  0 or null for unlimited.
        this.numberRows = null;
        // prop: numberColumns
        // Maximum number of columns in the legend.  0 or null for unlimited.
        this.numberColumns = null;
        // prop: seriesToggle
        // false to not enable series on/off toggling on the legend.
        // true or a fadein/fadeout speed (number of milliseconds or 'fast', 'normal', 'slow') 
        // to enable show/hide of series on click of legend item.
        this.seriesToggle = 'normal';
        // prop: seriesToggleReplot
        // True to replot the chart after toggling series on/off.
        // This will set the series show property to false.
        // This allows for rescaling or other maniplation of chart.
        // Set to an options object (e.g. {resetAxes: true}) for replot options.
        this.seriesToggleReplot = false;
        // prop: disableIEFading
        // true to toggle series with a show/hide method only and not allow fading in/out.  
        // This is to overcome poor performance of fade in some versions of IE.
        this.disableIEFading = true;
        // prop: toolTips
        // optional array of toolTip text corresponding to each pie slice
        this.toolTips = [];
        $.extend(true, this, options);
        
        if (this.seriesToggle) {
            $.jqplot.postDrawHooks.push(postDraw);
        }
    };
    
    // called with scope of legend
    $.jqplot.EnhancedPieLegendRenderer.prototype.draw = function(offsets, plot) {
        var legend = this;
        if (this.show) {
            var series = this._series;
            var s;
            var ss = 'position:absolute;';
            ss += (this.background) ? 'background:'+this.background+';' : '';
            ss += (this.border) ? 'border:'+this.border+';' : '';
            ss += (this.fontSize) ? 'font-size:'+this.fontSize+';' : '';
            ss += (this.fontFamily) ? 'font-family:'+this.fontFamily+';' : '';
            ss += (this.textColor) ? 'color:'+this.textColor+';' : '';
            ss += (this.marginTop != null) ? 'margin-top:'+this.marginTop+';' : '';
            ss += (this.marginBottom != null) ? 'margin-bottom:'+this.marginBottom+';' : '';
            ss += (this.marginLeft != null) ? 'margin-left:'+this.marginLeft+';' : '';
            ss += (this.marginRight != null) ? 'margin-right:'+this.marginRight+';' : '';
            this._elem = $('<table class="jqplot-table-legend" style="'+ss+'"></table>');
            if (this.seriesToggle) {
                this._elem.css('z-index', '3');
            }
        
            var pad = false, 
                reverse = false,
                nr, nc;
            var s = series[0];
            var slen = s.data.length;
            var colorGenerator = new $.jqplot.ColorGenerator(s.seriesColors);

            if (this.numberRows) {
                nr = this.numberRows;
                if (!this.numberColumns){
                    nc = Math.ceil(slen/nr);
                }
                else{
                    nc = this.numberColumns;
                }
            }
            else if (this.numberColumns) {
                nc = this.numberColumns;
                nr = Math.ceil(slen/this.numberColumns);
            }
            else {
                nr = slen;
                nc = 1;
            }
                
            var i, j, tr, td1, td2, lt, rs, div, div0, div1;
            var idx = 0;
            // check to see if we need to reverse
            for (i=series.length-1; i>=0; i--) {
                if (nc == 1 && series[i]._stack || series[i].renderer.constructor == $.jqplot.BezierCurveRenderer){
                    reverse = true;
                }
            }    
                
            for (i=0; i<nr; i++) {
                tr = $(document.createElement('tr'));
                tr.addClass('jqplot-table-legend');
                if (reverse){
                    tr.prependTo(this._elem);
                }
                else{
                    tr.appendTo(this._elem);
                }
                for (j=0; j<nc; j++) {
                    if (idx < slen){
                        lt = this.labels[idx] || s.data[idx][0].toString();
                        tt = this.toolTips[idx];
                        if (lt) {
                            var color = colorGenerator.next();
                            if (!reverse){
                                if (i>0){
                                    pad = true;
                                }
                                else{
                                    pad = false;
                                }
                            }
                            else{
                                if (i == nr -1){
                                    pad = false;
                                }
                                else{
                                    pad = true;
                                }
                            }
                            rs = (pad) ? this.rowSpacing : '0';

                            td1 = $(document.createElement('td'));
                            td1.addClass('jqplot-table-legend jqplot-table-legend-swatch');
                            td1.css({textAlign: 'center', paddingTop: rs});

                            div0 = $(document.createElement('div'));
                            div0.addClass('jqplot-table-legend-swatch-outline');
                            if (tt !== undefined) {
                                div0.attr("title", tt);
                            }

                            div1 = $(document.createElement('div'));
                            div1.addClass('jqplot-table-legend-swatch');
                            div1.css({backgroundColor: color, borderColor: color});

                            td1.append(div0.append(div1));

                            td2 = $(document.createElement('td'));
                            td2.addClass('jqplot-table-legend jqplot-table-legend-label');
                            td2.css('paddingTop', rs);
                            if (tt !== undefined) {
                                td2.attr("title", tt);
                            }
                    
                            if (this.escapeHtml){
                                td2.text(lt);
                            }
                            else {
                                td2.html(lt);
                            }
                            if (reverse) {
                                if (this.showLabels) {td2.prependTo(tr);}
                                if (this.showSwatches) {td1.prependTo(tr);}
                            }
                            else {
                                if (this.showSwatches) {td1.appendTo(tr);}
                                if (this.showLabels) {td2.appendTo(tr);}
                            }
                            
                            if (this.seriesToggle) {

                                var speed;
                                if (typeof(this.seriesToggle) === 'string' || typeof(this.seriesToggle) === 'number') {
                                    if (!$.jqplot.use_excanvas || !this.disableIEFading) {
                                        speed = this.seriesToggle;
                                    }
                                } 
                                if (this.showSwatches) {
                                    td1.bind('click', {series:s, index:idx, speed:speed, plot: plot, replot:this.seriesToggleReplot}, handleToggle);
                                    td1.addClass('jqplot-seriesToggle');
                                }
                                if (this.showLabels)  {
                                    td2.bind('click', {series:s, index:idx, speed:speed, plot: plot, replot:this.seriesToggleReplot}, handleToggle);
                                    td2.addClass('jqplot-seriesToggle');
                                }

                                // for slices that are already hidden, add the hidden class
                                if (s.showSlice[idx] === false && s.showLabel) {
                                    td1.addClass('jqplot-series-hidden');
                                    td2.addClass('jqplot-series-hidden');
                                }
                            }
                            
                            pad = true;
                        }
                    }
                    idx++;
                }
                
                td1 = td2 = div0 = div1 = null;   
            }
        }
        return this._elem;
    };

    var handleToggle = function (ev) {
        var d = ev.data,
            replot = d.replot,
            plot = d.plot,
            idx = d.index;

        d.series.showSlice[idx] = (d.series.showSlice[idx] === false) ? true : false;
    
        var opts = {};

        if ($.isPlainObject(replot)) {
            $.extend(true, opts, replot);
        }

        plot.replot(opts);
    };

    // called with scope of plot.
    var postDraw = function () {
        if (this.legend.renderer.constructor == $.jqplot.EnhancedPieLegendRenderer && this.legend.seriesToggle) {
            var e = this.legend._elem.detach();
            this.eventCanvas._elem.after(e);
        }
    };
})(jQuery);
