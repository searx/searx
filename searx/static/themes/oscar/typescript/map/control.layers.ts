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

module searx {
    export module map {
        export module control {
            // https://github.com/openstreetmap/openstreetmap-website/blob/master/app/assets/javascripts/leaflet.layers.js
            // https://github.com/Leaflet/Leaflet/blob/master/src/control/Control.Layers.js
            // http://rowanwinsemius.id.au/blog/add-and-remove-layers-with-leaflet-js/
            export interface LayersOptions extends L.ControlOptions {
                layers?: layer.iMapLayer[];
		    }


            export class Layers extends L.Control {
                public options: LayersOptions;
                public layers: layer.iMapLayer[];
                public map;
            
                constructor(options?: LayersOptions) {
                    super(options);
                    this.options = options;
                    this.layers = options.layers;
                }
                
                onAdd(map: L.Map): HTMLElement {
                    this.map = map;
	                var $container = $('<div>')
	                  .attr('class', 'control-layers');
            
                    var map_ui = $(map.getContainer()).parent().find('.map-ui');
            
	                var button = $('<a>')
	                  .attr('class', 'control-button')
	                  .attr('href', '#')
	                  .attr('title', 'layers-title')
	                  .html('<span class="icon glyphicon glyphicon-th-list"></span>')
	                  //.on('click', toggle)
	                  .click(function() {
	                       if(map_ui.css('display') != 'block') {
		                        map_ui.css('display', 'block');
		                    } else {
		                        map_ui.css('display', 'none');
		                    }
		                    
		                    // don't reload the page
		                    return false;
	                  })
	                  .appendTo($container);
            
                    var panel = $('<p>').appendTo(map_ui.find('.layers-ui .panel-body'));
                    for(var layerId in this.layers) {
                        var mapLayer: layer.iMapLayer = this.layers[layerId];
                        panel.append(this.getLayerSelector(mapLayer));
                        panel.append(' ' + mapLayer.name + '<br\>');
                    
                    }
            
                    return $container[0];
                }
                
                getLayerSelector(mapLayer: layer.iMapLayer): any {
                        var layerSelection = $(document.createElement('input'));
                        layerSelection.attr('type', 'radio');
                        layerSelection.attr('name', 'maplayer');
                        layerSelection.attr('value', mapLayer.code);
                        if(this.map.hasLayer(mapLayer.layer))
                            layerSelection.attr('checked', '1');

                        var thisMap = this.map;
                        var thisLayers = this.layers;
                        layerSelection.click(function() {
                            console.log(mapLayer);
                            for(var i in thisLayers) {
                                if(thisLayers[i] == mapLayer)
                                    thisMap.addLayer(mapLayer.layer);
                                else
                                    thisMap.removeLayer(thisLayers[i].layer);
                            }
                        });
                        return layerSelection;
                }
            }

            export function layers(options) {
                return new Layers(options);
            };


        }
    }
}