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

module searx {
    export module map {
    
        /**
          * get layers which are used on the map
          */
        export function getDefaultLayers(): layer.iMapLayer[] {
            return [
                new layer.Mapnik(),
                new layer.CycleMap(),
                new layer.TransportMap(),
                new layer.LandscapeMap(),
                new layer.OutdoorsMap(),
                new layer.HOT(),
                new layer.MapQuestOpen(),
                new layer.MapquestOpenAerial(),
                new layer.ArcGISAerial(),
            ];
        }
    
        export module layer {
            var osmAttribution: string = 'Map data © <a href="https://openstreetmap.org">OpenStreetMap</a> contributors';
        
            
            /**
              *
              */
	        export class Mapnik implements iMapLayer {
                public name: string = "Mapnik";
                public code: string = "M";
                public layer: L.TileLayer;
                
                constructor() {
                    this.layer = new L.TileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                        minZoom: 1, 
                        maxZoom: 19,
                        subdomains: ['a','b','c'],
                        attribution: osmAttribution
                    });
                }
            }
            
            
            /**
              * http://www.thunderforest.com/opencyclemap/
              */
            export class CycleMap implements iMapLayer {
                public name: string = "CycleMap";
                public code: string = "C";
                public layer: L.TileLayer;
                
                public static attribution: string = osmAttribution + ' | Tiles courtesy of <a href="http://www.thunderforest.com/" target="blank">Andy Allan</a>';
                
                constructor() {
                    this.layer = new L.TileLayer('http://{s}.tile.opencyclemap.org/cycle/{z}/{x}/{y}.png', {
                        minZoom: 1, 
                        maxZoom: 18,
                        subdomains: ['a','b','c'],
                        attribution: CycleMap.attribution
                    });
                }
            }


            /**
              * http://www.thunderforest.com/transport/
              */
            export class TransportMap implements iMapLayer {
                public name: string = "TransportMap";
                public code: string = "T";
                public layer: L.TileLayer;
                
                public static attribution: string = osmAttribution + ' | Tiles courtesy of <a href="http://www.thunderforest.com/" target="blank">Andy Allan</a>';
                
                constructor() {
                    this.layer = new L.TileLayer('http://{s}.tile.thunderforest.com/transport/{z}/{x}/{y}.png', {
                        minZoom: 1, 
                        maxZoom: 18,
                        subdomains: ['a','b','c'],
                        attribution: TransportMap.attribution
                    });
                }
            }
            
            
            /**
              * http://www.thunderforest.com/landscape/
              */
            export class LandscapeMap implements iMapLayer {
                public name: string = "Landscape";
                public code: string = "L";
                public layer: L.TileLayer;
                
                public static attribution: string = osmAttribution + ' | Tiles courtesy of <a href="http://www.thunderforest.com/" target="blank">Andy Allan</a>';
                
                constructor() {
                    this.layer = new L.TileLayer('http://{s}.tile.thunderforest.com/landscape/{z}/{x}/{y}.png', {
                        minZoom: 1, 
                        maxZoom: 18,
                        subdomains: ['a','b','c'],
                        attribution: LandscapeMap.attribution
                    });
                }
            }
            
            
            /**
              * http://www.thunderforest.com/outdoors/
              */
            export class OutdoorsMap implements iMapLayer {
                public name: string = "Outdoors";
                public code: string = "O";
                public layer: L.TileLayer;
                
                public static attribution: string = osmAttribution + ' | Tiles courtesy of <a href="http://www.thunderforest.com/" target="blank">Andy Allan</a>';
                
                constructor() {
                    this.layer = new L.TileLayer('http://{s}.tile.thunderforest.com/outdoors/{z}/{x}/{y}.png', {
                        minZoom: 1, 
                        maxZoom: 18,
                        subdomains: ['a','b','c'],
                        attribution: OutdoorsMap.attribution
                    });
                }
            }
            
            
            /**
              *
              */
            export class HOT implements iMapLayer {
                public name: string = "HOT";
                public code: string = "H";
                public layer: L.TileLayer;
                
                public static attribution: string = osmAttribution + ' | Tiles courtesy of <a href="http://hot.openstreetmap.org/" target="_blank">Humanitarian OpenStreetMap Team</a>';
                
                constructor() {
                    this.layer = new L.TileLayer('http://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png', {
                        minZoom: 1, 
                        maxZoom: 20,
                        subdomains: ['a','b','c'],
                        attribution: HOT.attribution
                    });
                }
            }
                        
           
            /**
              *
              */
            export class MapQuestOpen implements iMapLayer {
                public name: string = "MapQuest Open";
                public code: string = "Q";
                public layer: L.TileLayer;


                public static attribution: string = osmAttribution + ' | Tiles Courtesy of <a href="http://www.mapquest.com/" target="_blank">MapQuest</a> <img src="http://developer.mapquest.com/content/osm/mq_logo.png">';
                
                constructor() {
                    this.layer = new L.TileLayer('http://otile{s}.mqcdn.com/tiles/1.0.0/map/{z}/{x}/{y}.jpg', {
                        minZoom: 1, 
                        maxZoom: 18,
                        subdomains: ['1','2','3','4'],
                        attribution: MapQuestOpen.attribution
                    });
                }
            }


            /**
              *
              */       
            export class MapquestOpenAerial implements iMapLayer {
                public name: string = "MapQuest Open Aerial";
                public code: string = "QA";
                public layer: L.TileLayer;

                public static attribution: string = MapQuestOpen.attribution + ' | Portions Courtesy NASA/JPL-Caltech and U.S. Depart. of Agriculture, Farm Service Agency';
                
                constructor() {
                    this.layer = new L.TileLayer('http://otile{s}.mqcdn.com/tiles/1.0.0/sat/{z}/{x}/{y}.jpg', {
                        minZoom: 1, 
                        maxZoom: 11,
                        subdomains: ['1','2','3','4'],
                        attribution: MapquestOpenAerial.attribution
                    });
                }
            }
            
            
            /**
              *
              */
            export class ArcGISAerial implements iMapLayer {
                public name: string = "ArcGIS Aerial";
                public code: string = "AA";
                public layer: L.TileLayer;
                
                public static attribution: string = osmAttribution + ' | Source: Esri, DigitalGlobe, GeoEye, Earthstar Geographics, CNES/Airbus DS, USDA, USGS, AEX, Getmapping, Aerogrid, IGN, IGP, swisstopo, and the GIS User Community';
                
                constructor() {
                    this.layer = new L.TileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
                        minZoom: 1, 
                        maxZoom: 18,
                        attribution: ArcGISAerial.attribution
                    });
                }
            }


            export interface iMapLayer {
                /**
                  * name of layer, which is displayed in menue
                  */
                name: string;
                
                /**
                  * unique code for every layer (to set links)
                  */
                code: string;
                
                /**
                  * leaflet layer which is containting all the data about the layer
                  */
                layer: L.TileLayer;
            }
        }
    }
}