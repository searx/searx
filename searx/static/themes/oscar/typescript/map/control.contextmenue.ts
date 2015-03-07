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
              * https://github.com/aratcliffe/Leaflet.contextmenu/blob/master/src/Map.ContextMenu.js
              */
            export class Contextmenue {
                public _options: ContextmenueOptions;
                public _map: L.Map;
                public _container: JQuery;
                public _visible: boolean;
                public _containerPoint: L.LatLng;
            
                constructor(options?: ContextmenueOptions) {
                    this._options = options;
                }
                
                addMenue(map: L.Map) {
                    // get map
                    this._map = map;
                    
                    // create container which is showing the contextmenue
                    this._container = $('<div>').addClass('leaflet-contextmenu')
                        .css('zIndex','10000')
                        .css('position','absolute')
                        .css('display', 'none');
                    this._visible = false;
                    
                    // add contextmenue entities
                    if(this._options.routingMenue === true) {
	                    var itemSetStart: JQuery = this._createItem('Set as start', 
	                       'leaflet-contextmenu-item-disabled', 
	                       this._container, function(){}, this);
	                    var itemSetIntermediate: JQuery = this._createItem('Set intermediate', 
	                       'leaflet-contextmenu-item-disabled', 
	                       this._container, function(){}, this);
	                    var itemSetEnd: JQuery = this._createItem('Set as end', 
	                       'leaflet-contextmenu-item-disabled', 
	                       this._container, function(){}, this);
	                    this._container.append('<div class="leaflet-contextmenu-separator"></div>');
                    }
                    var itemShowCoordinates: JQuery = this._createItem('Show coordinates', 
                        '', 
                        this._container, this._showCoordinates, this);
                    var itemCenterMap: JQuery = this._createItem('Center map here', 
                        '', 
                        this._container, this._centerMap, this);
                    
                    // prevent not desired events
                    var stop = L.DomEvent.stopPropagation;
                    this._container.click(stop)
                        .mousedown(stop)
                        .dblclick(stop)
                        .click(L.DomEvent.preventDefault);
                    
                    // add container to map-div
                    $(map.getContainer()).append(this._container);
                    
                    // add events which show or hide the contextmenue
                    this._map.on({
                        contextmenu: this._show,
                        mouseout: this._hide,
                        mousedown: this._hide,
                        movestart: this._hide,
                        zoomstart: this._hide
                    }, this);
                    L.DomEvent.on(map.getContainer(), 'keydown', this._onKeyDown, this);
                }
                
                _createItem(html: string, className: string, container: JQuery, fn, context): JQuery {
                    // create link and add all element handlers
                    var item: JQuery = $('<a>')
                        .addClass('leaflet-contextmenu-item')
                        .addClass(className)
                        .attr('href', '#')
                        .html(html)
                        .click(L.DomEvent.preventDefault);
                    
                    // TODO: using JQuery Syntax
                    L.DomEvent.on(item[0], 'click', fn, context);
                    
                    this._container.append(item);
                    
                    return item;
                }
                
                _showCoordinates(e) {					
                    // create content of popup
                    var content: JQuery = $('<table>')
                       .addClass('table-condensed')
                       .addClass('table-hover')
                       .append($('<tr>')
                           .append($('<td><b>Lat</b></td>'))
                           .append($('<td>')
                           .addClass('cursor-text')
            	           .html(this._containerPoint.lat.toFixed(6))
            		       )
            		   )
            		   .append($('<tr>')
                           .append($('<td><b>Lng</b></td>'))
                           .append($('<td>')
                               .addClass('cursor-text')
                               .html(this._containerPoint.lng.toFixed(6))
                           )
                        );

                    // show popup
                    var popup = L.popup()
                        .setLatLng(this._containerPoint)
                        .setContent(content.get(0))
                        .openOn(this._map);

                    // hide contextmenue
                    this._hide();
                }
                
                _centerMap(e) {
                    this._map.fire('dragstart');
                    this._map.setView(this._containerPoint);
                    this._map.fire('dragend');
                    
                    // hide contextmenue
                    this._hide();
                }
                
                isVisible(): boolean {
                    return this._visible;
                }
                
                _show(e) {
                    this._showAtPoint(e.containerPoint);
                }

                _showAtPoint(pt: L.Point) {
                    this._visible = true;
                    this._container.css('display', 'block');
                    
                    // as long as the contextmenue is visible, the map cursor is set to default
                    $(this._map.getContainer()).css('cursor', 'default');
                
                    this._setPosition(pt);
                }
                
                _setPosition(pt: L.Point) {
                    var mapSize: L.Point = this._map.getSize();
                    
                    // get position on map, where the mouse has clicked
                    var layerPoint = this._map.containerPointToLayerPoint(pt);
                    this._containerPoint = this._map.layerPointToLatLng(layerPoint);

                    // always show container inside map, so we have to check how to place it
                    if (pt.x + this._container.height() > mapSize.x) {
                        this._container.css('left','auto');
                        this._container.css('right', Math.max(mapSize.x - pt.x, 0) + 'px');
                    } else {
                        this._container.css('left', Math.max(pt.x, 0) + 'px');
                        this._container.css('right','auto');
                    }
                    
                    if (pt.y + this._container.width() > mapSize.y) {
                        this._container.css('top','auto')
                        this._container.css('bottom', Math.max(mapSize.y - pt.y, 0) + 'px');
                    } else {
                        this._container.css('top', Math.max(pt.y, 0) + 'px');
                        this._container.css('bottom', 'auto');
                    }
                }
            
                _hide() {
                    if (this._visible) {
                        this._visible = false;
                        this._container.css('display', 'none');
                        $(this._map.getContainer()).css('cursor', 'grab');
                    }
                }
                
                _onMouseDown(e) {
                    this._hide();
                }
            
                _onKeyDown(e) {
                    var key: number = e.keyCode;
            
                    // If ESC pressed and context menu is visible hide it 
                    if (key === 27) {
                        this._hide();
                    }
                }
            }
        
            export interface ContextmenueOptions extends L.ControlOptions {
                routingMenue?: boolean;
            }
        
            export function contextmenue(options) {
                return new Contextmenue(options);
            };
        }
    }
}