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


            // TODO: https://github.com/openstreetmap/openstreetmap-website/blob/master/app/assets/javascripts/leaflet.layers.js

            // https://github.com/openstreetmap/openstreetmap-website/blob/master/app/assets/javascripts/leaflet.zoom.js
            export class Zoom extends L.Control {
                _map;
                _zoomInButton;
                _zoomOutButton;
                
                constructor(options?: L.ControlOptions) {
                    super(options);
                }
                
                onAdd(map) {
                    var zoomName = 'zoom',
	                container = L.DomUtil.create('div', zoomName);
	                this._map = map;
	                this._zoomInButton = this._createButton(
	                   '', 'zoom-in', 'plus zoomin', container, this._zoomIn, this);
	                this._zoomOutButton = this._createButton(
	                   '', 'zoom-out', 'minus zoomout', container, this._zoomOut, this);
	                map.on('zoomend zoomlevelschange', this._updateDisabled, this);
	                return container;
                }
                
                onRemove(map) {
                    map.off('zoomend zoomlevelschange', this._updateDisabled, this);
                }
                
                _zoomIn(e) {
                    this._map.zoomIn(e.shiftKey ? 3 : 1);
                }
                
                _zoomOut(e) {
                this._map.zoomOut(e.shiftKey ? 3 : 1);
                }
                
                _createButton(html, title, className, container, fn, context) {
                    var link = L.DomUtil.create('a', 'control-button ' + className, container);
                    link.innerHTML = html;
                    //link.href = '#';
                    //link.title = title;
                    L.DomUtil.create('span', 'icon glyphicon glyphicon-' + className, link);
                    var stop = L.DomEvent.stopPropagation;
                    L.DomEvent.on(link, 'click', stop);
                    L.DomEvent.on(link, 'mousedown', stop);
                    L.DomEvent.on(link, 'dblclick', stop);
                    L.DomEvent.on(link, 'click', L.DomEvent.preventDefault);
                    L.DomEvent.on(link, 'click', fn, context);
                    return link;
                }
                
                _updateDisabled() {
	                var map = this._map,
	                className = 'leaflet-disabled';
	                L.DomUtil.removeClass(this._zoomInButton, className);
	                L.DomUtil.removeClass(this._zoomOutButton, className);
	                if (map._zoom === map.getMinZoom()) {
	                   L.DomUtil.addClass(this._zoomOutButton, className);
	                }
	                if (map._zoom === map.getMaxZoom()) {
	                    L.DomUtil.addClass(this._zoomInButton, className);
	                }
                }
            }
            
            export function zoom(options) {
                return new Zoom(options);
            };
        }
    }
}