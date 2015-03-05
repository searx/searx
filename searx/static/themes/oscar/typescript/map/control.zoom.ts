/**
 * searx is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * searx is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with searx. If not, see < http://www.gnu.org/licenses/ >.
 *
 * (C) 2015 by Thomas Pointhuber, <thomas.pointhuber@gmx.at>
 */

/// <reference path="../../../../typescript/leaflet.d.ts" />
/// <reference path="../../../../typescript/jquery.d.ts" />
/// <reference path="../oscar.d.ts" />

module searx {
    export module map {
        export module control {
            /**
              * Original implementation:
              * https://github.com/openstreetmap/openstreetmap-website/blob/master/app/assets/javascripts/leaflet.zoom.js
              */
            export class Zoom extends L.Control {
                public _map: L.Map;
                public _zoomInButton: JQuery;
                public _zoomOutButton: JQuery;
                
                constructor(options?: L.ControlOptions) {
                    super(options);
                }
                
                onAdd(map: L.Map): HTMLElement {
                    // get map
                    this._map = map;
                
                    // create container which is storing the zoom buttons
                    var container: JQuery = $('<div>').addClass('zoom');
                    
                    // create zoomIn Button
                    this._zoomInButton = this._createButton(
                       '', 'zoom-in', 'plus zoomin', container, this._zoomIn, this);
                    
                    // create zoomOut Button
                    this._zoomOutButton = this._createButton(
                       '', 'zoom-out', 'minus zoomout', container, this._zoomOut, this);
                    
                    // add eventlisteners
                    this._map.on('zoomend zoomlevelschange', this._updateDisabled, this);
                    
                    // return zoom-buttons
                    return container[0];
                }
                
                onRemove(map: L.Map) {
                    // remove eventlisteners
                    map.off('zoomend zoomlevelschange', this._updateDisabled, this);
                }
                
                _zoomIn(e) {
                    this._map.zoomIn(e.shiftKey ? 3 : 1);
                }
                
                _zoomOut(e) {
                    this._map.zoomOut(e.shiftKey ? 3 : 1);
                }
                
                _createButton(html: string, title: string, className: string, container: JQuery, fn, context): JQuery {
                    var stop = L.DomEvent.stopPropagation;
                    
                    // create link and add all element handlers
                    var link: JQuery = $('<a>')
                        .addClass('control-button')
                        .addClass(className)
                        .attr('href', '#')
                        .html('<span class="icon glyphicon glyphicon-' + className + '"></span>')
                        .click(stop)
                        .mousedown(stop)
                        .dblclick(stop)
                        .click(L.DomEvent.preventDefault);
                    
                    // TODO: using JQuery Syntax
                    L.DomEvent.on(link[0], 'click', fn, context);
                    
                    container.append(link);
                    
                    return link;
                }
                
                _updateDisabled() {
                    var className = 'leaflet-disabled';
                    this._zoomInButton.removeClass(className);
                    this._zoomOutButton.removeClass(className);

                    // disable button if it is useless
                    if (this._map.getZoom() === this._map.getMinZoom()) {
                       this._zoomOutButton.addClass(className);
                    }
                    if (this._map.getZoom() === this._map.getMaxZoom()) {
                        this._zoomInButton.addClass(className);
                    }
                }
            }
            
            export function zoom(options) {
                return new Zoom(options);
            };
        }
    }
}