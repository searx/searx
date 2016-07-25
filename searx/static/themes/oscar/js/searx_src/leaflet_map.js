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
 * (C) 2014 by Thomas Pointhuber, <thomas.pointhuber@gmx.at>
 */

$(document).ready(function(){
    $(".searx_overpass_request").on( "click", function( event ) {
        var overpass_url = "https://overpass-api.de/api/interpreter?data=";
        var query_start = overpass_url + "[out:json][timeout:25];(";
        var query_end = ");out meta;";
        
        var osm_id = $(this).data('osm-id');
        var osm_type = $(this).data('osm-type');
        var result_table = $(this).data('result-table');
        var result_table_loadicon = "#" + $(this).data('result-table-loadicon');
        
        // tags which can be ignored
        var osm_ignore_tags = [ "addr:city", "addr:country", "addr:housenumber", "addr:postcode", "addr:street" ];
        
        if(osm_id && osm_type && result_table) {
            result_table = "#" + result_table;
            var query = null;
            switch(osm_type) {
                case 'node':
                    query = query_start + "node(" + osm_id + ");" + query_end;
                    break;
                case 'way':
                    query = query_start + "way(" + osm_id + ");" + query_end;
                    break;
                case 'relation':
                    query = query_start + "relation(" + osm_id + ");" + query_end;
                    break;
                default:
                    break;
            }
            if(query) {
                //alert(query);
                var ajaxRequest = $.ajax( query )
                .done(function( html) {
                    if(html && html.elements && html.elements[0]) {
                        var element = html.elements[0];
                        var newHtml = $(result_table).html();
                        for (var row in element.tags) {
                            if(element.tags.name === null || osm_ignore_tags.indexOf(row) == -1) {
                                newHtml += "<tr><td>" + row + "</td><td>";
                                switch(row) {
                                    case "phone":
                                    case "fax":
                                        newHtml += "<a href=\"tel:" + element.tags[row].replace(/ /g,'') + "\">" + element.tags[row] + "</a>";
                                        break;
                                    case "email":
                                        newHtml += "<a href=\"mailto:" + element.tags[row] + "\">" + element.tags[row] + "</a>";
                                        break;
                                    case "website":
                                    case "url":
                                        newHtml += "<a href=\"" + element.tags[row] + "\">" + element.tags[row] + "</a>";
                                        break;
                                    case "wikidata":
                                        newHtml += "<a href=\"https://www.wikidata.org/wiki/" + element.tags[row] + "\">" + element.tags[row] + "</a>";
                                        break;
                                    case "wikipedia":
                                        if(element.tags[row].indexOf(":") != -1) {
                                            newHtml += "<a href=\"https://" + element.tags[row].substring(0,element.tags[row].indexOf(":")) + ".wikipedia.org/wiki/" + element.tags[row].substring(element.tags[row].indexOf(":")+1) + "\">" + element.tags[row] + "</a>";
                                            break;
                                        }
                                    /* jshint ignore:start */
                                    default:
                                    /* jshint ignore:end */
                                        newHtml += element.tags[row];
                                        break;
                                }
                                newHtml += "</td></tr>";
                            }
                        }
                        $(result_table).html(newHtml);
                        $(result_table).removeClass('hidden');
                        $(result_table_loadicon).addClass('hidden');
                    }
                })
                .fail(function() {
                    $(result_table_loadicon).html($(result_table_loadicon).html() + "<p class=\"text-muted\">could not load data!</p>");
                });
            }
        }

        // this event occour only once per element
        $( this ).off( event );    
    });

    $(".searx_init_map").on( "click", function( event ) {
        var leaflet_target = $(this).data('leaflet-target');
        var map_lon = $(this).data('map-lon');
        var map_lat = $(this).data('map-lat');
        var map_zoom = $(this).data('map-zoom');
        var map_boundingbox = $(this).data('map-boundingbox');
        var map_geojson = $(this).data('map-geojson');

        require(['leaflet-0.7.3.min'], function(leaflet) {
            if(map_boundingbox) {
                southWest = L.latLng(map_boundingbox[0], map_boundingbox[2]);
                northEast = L.latLng(map_boundingbox[1], map_boundingbox[3]);
                map_bounds = L.latLngBounds(southWest, northEast);
            }

            // TODO hack
            // change default imagePath
            L.Icon.Default.imagePath = 	"./static/themes/oscar/img/map";

            // init map
            var map = L.map(leaflet_target);

            // create the tile layer with correct attribution
	    var osmMapnikUrl='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
	    var osmMapnikAttrib='Map data © <a href="https://openstreetmap.org">OpenStreetMap</a> contributors';
	    var osmMapnik = new L.TileLayer(osmMapnikUrl, {minZoom: 1, maxZoom: 19, attribution: osmMapnikAttrib});

	    var osmWikimediaUrl='https://maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png';
	    var osmWikimediaAttrib = 'Wikimedia maps beta | Maps data © <a href="https://openstreetmap.org">OpenStreetMap</a> contributors';
	    var osmWikimedia = new L.TileLayer(osmWikimediaUrl, {minZoom: 1, maxZoom: 19, attribution: osmWikimediaAttrib});

            // init map view
            if(map_bounds) {
                // TODO hack: https://github.com/Leaflet/Leaflet/issues/2021
                setTimeout(function () {
                    map.fitBounds(map_bounds, {
                        maxZoom:17
                    });
                }, 0);
            } else if (map_lon && map_lat) {
                if(map_zoom) 
                    map.setView(new L.LatLng(map_lat, map_lon),map_zoom);
                else
                    map.setView(new L.LatLng(map_lat, map_lon),8);
            }

	        map.addLayer(osmMapnik);
	        
	        var baseLayers = {
             "OSM Mapnik": osmMapnik/*,
             "OSM Wikimedia": osmWikimedia*/
            };

            L.control.layers(baseLayers).addTo(map);


            if(map_geojson)
                L.geoJson(map_geojson).addTo(map);
            /*else if(map_bounds)
                L.rectangle(map_bounds, {color: "#ff7800", weight: 3, fill:false}).addTo(map);*/
        });

        // this event occour only once per element
        $( this ).off( event );
    });
});  
