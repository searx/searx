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

/// <reference path="../../../typescript/jquery.d.ts" />
/// <reference path="oscar.d.ts" />
/// <reference path="map/Map.ts" />
/// <reference path="osm/element_request.ts" />
/// <reference path="osm/datatypes.ts" />

$(document).ready(function() {

    $(".searx_init_map").click(function( event: string ) {
        var thisElement: JQuery = $(this);
        
        // TODO hack: https://github.com/Leaflet/Leaflet/issues/2021
        setTimeout(function(){
            var targetId: string = thisElement.data('leaflet-target');
    
            // calculate boundingbox if possible
            var target_boundingbox: L.LatLngBounds = null;
            if(thisElement.data('map-boundingbox')) {    
                target_boundingbox = L.latLngBounds(
                    L.latLng(
                        thisElement.data('map-boundingbox')[0], 
                        thisElement.data('map-boundingbox')[2]
                    ),
                    L.latLng(
                        thisElement.data('map-boundingbox')[1], 
                        thisElement.data('map-boundingbox')[3]
                    )
                );
            }
    
            // create map
            var mapObj: searx.map.Map = new searx.map.Map(targetId, {
                latLng:     new L.LatLng(thisElement.data('map-lat'), thisElement.data('map-lng')),
                zoom:       thisElement.data('map-zoom'),
                geojson:    thisElement.data('map-geojson'),
                boundingbox: target_boundingbox,
                routingMenue: false
            });
	
        }, 0);
 
        // this event occour only once per element
        $(this).off( event );
    });


    $(".searx_overpass_request").click(function( event: string ) {
        var thisElement: JQuery = $(this);
        var loadIcon: JQuery = $("#" + thisElement.data('result-table-loadicon'));
        var resultTable = $("#" + $(this).data('result-table'));

        var osmId: number = $(this).data('osm-id');
        var osmType: searx.osm.osmTypes = searx.osm.getOsmTypeFromString($(this).data('osm-type'));
        
        // do request
        searx.osm.overpassApiElementRequest(osmId, osmType, {
            success: function(element: searx.osm.osmElement): void {
                // display value-key pairs
                for(var tagId in element.tags) {
                    // don't display the keys which are defined here:
                    if([ "addr:city", "addr:country", "addr:housenumber", "addr:postcode", "addr:street"
                       ].indexOf(element.tags[tagId].key) != -1)
                        continue;
                
                    var row: string = "<td>" + element.tags[tagId].key + "</td>" + 
                                      "<td>" + searx.osm.formateValues(element.tags[tagId]).join(';') + "</td>";
                    resultTable.append("<tr>" + row + "</tr");
                }
                
                resultTable.removeClass('hidden');
                loadIcon.addClass('hidden');
            },
            
            error: function(): void {
                loadIcon.append("<p class=\"text-muted\">could not load data!</p>");
            }
        });
        
        // this event occour only once per element
        $( this ).off( event );    
    });
});