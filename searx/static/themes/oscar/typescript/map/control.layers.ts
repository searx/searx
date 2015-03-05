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
/// <reference path="layers.ts" />
/// <reference path="map_panel.ts" />

module searx {
    export module map {
        export module control {
            /**
              * Original implementation:
              * https://github.com/openstreetmap/openstreetmap-website/blob/master/app/assets/javascripts/leaflet.layers.js
              */
            export class Layers extends L.Control {
                public _options: LayersOptions;
                public _layers: layer.iMapLayer[];
                public _map: L.Map;
            
                constructor(options?: LayersOptions) {
                    super(options);
                    this._options = options;
                    this._layers = options.layers;
                }
                
                onAdd(map: L.Map): HTMLElement {
                    // get map
                    this._map = map;
            
                    // get map_ui and layers_ui
                    var map_ui: JQuery = $(map.getContainer()).parent().find('.map-ui');
                    var layers_ui: JQuery = map_ui.find('.layers-ui');
                
                    // create container which is storing the layers button
                    var container: JQuery = $('<div>').addClass('control-layers');
            
                    // create control button and add it to the container div
                    var button: JQuery = $('<a>')
                        .addClass('control-button')
                        .attr('href', '#')
                        // TODO .attr('title', 'layers-title')
                        .html('<span class="icon glyphicon glyphicon-th-list"></span>')
                        .click(function() {
                            // toggle ui
                            if(togglePanelUi(map_ui, 'layers-ui'))
                                button.addClass('active');
                            else
                                button.removeClass('active');
                            
                            // TODO hack: https://github.com/Leaflet/Leaflet/issues/2021
                            setTimeout(function(){
                                map.invalidateSize({
                                    pan: false
                                });
                            }, 0);

                            // don't reload the page
                            return false;
                        })
                       .appendTo(container);
                    
                    // close panel if close button is clicked
                    layers_ui.find('.close').click(function() {
                        hidePanelUi(map_ui);
                        button.removeClass('active');
                        // TODO hack: https://github.com/Leaflet/Leaflet/issues/2021
                        setTimeout(function(){
                            map.invalidateSize({
                                    pan: false
                            });
                        }, 0);
                        
                        // don't reload the page
                        return false;
                    });
            
                    // create layer-control
                    var panel: JQuery = $('<p>').appendTo(layers_ui.find('.panel-body'));
                    for(var layerId in this._layers) {
                        // create single baselayer selector and add them to panel
                        var mapLayer: layer.iMapLayer = this._layers[layerId];
                        panel.append(this._getLayerSelector(mapLayer));
                        panel.append(' ' + mapLayer.name + '<br\>');
                    }
            
                    // return layers-button
                    return container[0];
                }
                
                _getLayerSelector(mapLayer: layer.iMapLayer): any {
                    // create layer-selector
                    var layerSelection: JQuery = $(document.createElement('input'))
                        .attr('type', 'radio')
                        .attr('name', 'maplayer')
                        .attr('value', mapLayer.code);
                    
                    // check if layer is already activated in leaflet
                    if(this._map.hasLayer(mapLayer.layer))
                        layerSelection.attr('checked', '1');

                    // add click event
                    var mapHelp: L.Map = this._map;
                    var layersHelp: layer.iMapLayer[] = this._layers;
                    layerSelection.click(function() {
                        // hide all other baseLayers except the selected one
                        for(var i in layersHelp) {
                            if(layersHelp[i] == mapLayer)
                                mapHelp.addLayer(mapLayer.layer);
                            else
                                mapHelp.removeLayer(layersHelp[i].layer);
                        }
                    });

                    // return created layer-selector
                    return layerSelection;
                }
            }
            
            export interface LayersOptions extends L.ControlOptions {
                layers?: layer.iMapLayer[];
            }

            export function layers(options) {
                return new Layers(options);
            };


        }
    }
}