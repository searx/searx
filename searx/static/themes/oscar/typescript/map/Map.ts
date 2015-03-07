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
/// <reference path="../oscar.d.ts" />
/// <reference path="layers.ts" />
/// <reference path="icons.ts" />
/// <reference path="control.zoom.ts" />
/// <reference path="control.layers.ts" />
/// <reference path="control.contextmenue.ts" />

module searx {
    export module map {
        export class Map {
            public map: L.Map;
            public layers: layer.iMapLayer[];
            public contextmenue: control.Contextmenue;

 
            constructor(mapId: string, options?: MapOptions) {
                this.init(mapId, options);
            }


            /**
              * init map
              *
              * @param mapId id which is the main-div of the map
              * @param options special setting which can change the map-view
              */
            init(mapId: string, options?: MapOptions): void {
            
                // TODO hack
                // change default imagePath
                L.Icon.Default.imagePath = "./static/img/map";

                // init map, using id of main-div
                this.map = L.map(mapId, {
                    zoomControl: false
                });

                // set default-view of map
                this.setDefaultView(options);

                // load layers
                if(options.layers)
                    this.layers = options.layers;
                else
                    this.layers = map.getDefaultLayers();

                // get default layer code
                var defaultLayerCode = 'M';
                if(options.defaultLayerCode)
                    defaultLayerCode = options.defaultLayerCode;

                // get default layer
                var default_layer: layer.iMapLayer = this.getLayerByCode(defaultLayerCode);
                
                // set default layer if possible, otherwise using first layer in array
                if(default_layer !== null)
                    this.map.addLayer(default_layer.layer);
                else
                    this.map.addLayer(this.layers[0].layer);

                // add controls
                this.map.addControl(control.zoom({position: 'topright'}));
                this.map.addControl(control.layers({position: 'topright', layers: this.layers}));
                //this.map.addControl(control.contextmenue({}));
                
                this.contextmenue = control.contextmenue({
                    routingMenue: options.routingMenue
                });
                this.contextmenue.addMenue(this.map);
                
                // create zoom to result menue entry
                if(options.boundingbox || options.latLng) {
                    var itemSetDefaultView: JQuery = this.contextmenue._createItem('zoom to result', 
                        'leaflet-contextmenu-item-disabled', 
                        this.contextmenue._container, 
                        function() {
                            this.setDefaultView(options);
                            itemSetDefaultView.addClass('leaflet-contextmenu-item-disabled');
                        }, this);
                    
                    // add event to activate element on drag
                    this.map.on('dragend autopanstart resize', function() {
                        itemSetDefaultView.removeClass('leaflet-contextmenu-item-disabled');
                    });
                }

                // display geojson if possible
                if(options.geojson)
                    this.map.addLayer(L.geoJson(options.geojson));
            }
            
            
            setDefaultView(options?: MapOptions) {
                // set default-view of map
                if(options.boundingbox) {
                    // set boundingbox if possible
                    this.setBoundingbox(options.boundingbox);
                } else if(options.latLng) {
                    // otherwise using lat-lng if possible
                    if(options.zoom) 
                        this.map.setView(options.latLng, options.zoom);
                    else
                        this.map.setView(options.latLng, 8);
                } else {
                    // TODO using cookie to set default-view. Currently showing europe by default
                    this.map.setView(new L.LatLng(49, 7), 5);
                }
            }


            /**
              * set view of map to a specific boundingbox
              *
              * @param boundingbox Boundingbox which has to be fitted by map
              * @param maxZoom maximum zoom to achive this boundingbox
              */
            setBoundingbox(boundingbox: L.LatLngBounds, maxZoom: number = 17): void {
                var map: L.Map = this.map;
                // TODO hack: https://github.com/Leaflet/Leaflet/issues/2021
		        setTimeout(function(){
		                map.fitBounds(boundingbox, {
		                    maxZoom: maxZoom
		                });
                }, 0);
            }


            /**
              * get layer by code if possible
              *
              * @param layerCode code of layer
              * @return layer.iMapLayer, or null if nothing is found
              */
            getLayerByCode(layerCode: string): layer.iMapLayer {
                // search for the correct layer inside the array
                for(var id in this.layers) {
                    if(layerCode == this.layers[id].code)
                        return this.layers[id];
                }
                
                // return null if nothing is found
                return null;
            }
        }


        export interface MapOptions {
        
            /**
              * set other layers as used by default
              */
            layers?: layer.iMapLayer[];
            
            /**
              * code of layer, which should used by default
              */
            defaultLayerCode?: string;
        
            /**
              * define boundingbox which has to fit by the map-window
              */
            boundingbox?: L.LatLngBounds;
            
            /**
              * define position which has to be the center of map
              */
            latLng?: L.LatLng;
            
            /**
              * define zoom of map
              */
            zoom?: number;
            
            /**
              * show geojson on map by default
              */
            geojson?: any;
            
            routingMenue?: boolean;
        }
    }
}