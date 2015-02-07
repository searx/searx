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
 * (C) 2014-2015 by Thomas Pointhuber, <thomas.pointhuber@gmx.at>
 */


searx.getLeafletLayers = function () {
    var layers = {};

    // create the tile layer with correct attribution
    var osmMapnikUrl = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
    var osmMapnikAttrib = 'Map data © <a href="https://openstreetmap.org">OpenStreetMap</a> contributors';
    layers.Mapnik = new L.TileLayer(osmMapnikUrl, {minZoom: 1, maxZoom: 19, attribution: osmMapnikAttrib});

    var osmMapquestUrl = 'http://otile{s}.mqcdn.com/tiles/1.0.0/map/{z}/{x}/{y}.jpg';
    var osmMapquestAttrib = osmMapnikAttrib + ' | Tiles Courtesy of <a href="http://www.mapquest.com/" target="_blank">MapQuest</a> <img src="http://developer.mapquest.com/content/osm/mq_logo.png">';
    layers.Mapquest = new L.TileLayer(osmMapquestUrl, {minZoom: 1, maxZoom: 18, subdomains: '1234', attribution: osmMapquestAttrib});

	var osmMapquestOpenAerialUrl='http://otile{s}.mqcdn.com/tiles/1.0.0/sat/{z}/{x}/{y}.jpg';
    var osmMapquestOpenAerialAttrib= osmMapquestAttrib + ' | Portions Courtesy NASA/JPL-Caltech and U.S. Depart. of Agriculture, Farm Service Agency';
	//layers.MapquestOpenAerial = new L.TileLayer(osmMapquestOpenAerialUrl, {minZoom: 1, maxZoom: 11, subdomains: '1234', attribution: osmMapquestOpenAerialAttrib});
	
    var ArcGISAerialUrl='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}';
    var ArcGISAerialAttrib= 'Source: Esri, DigitalGlobe, GeoEye, Earthstar Geographics, CNES/Airbus DS, USDA, USGS, AEX, Getmapping, Aerogrid, IGN, IGP, swisstopo, and the GIS User Community ';
    layers.ArcGIS = new L.TileLayer(ArcGISAerialUrl, {minZoom: 1, maxZoom: 18, attribution: ArcGISAerialAttrib});

    return layers;
};


searx.createLeafletMap = function (leaflet_target, options) {
    // check if layers are defined, otherwise use default Layers
    if(!options.layers) {
        options.layers = searx.getLeafletLayers();
    }
    
    // calculate boundingbox if possible
    if(options.boundingbox) {
        var southWest = L.latLng(options.boundingbox[0], options.boundingbox[2]);
        var northEast = L.latLng(options.boundingbox[1], options.boundingbox[3]);

        options.map_bounds = L.latLngBounds(southWest, northEast);
    }

    // TODO hack
    // change default imagePath
    L.Icon.Default.imagePath = "./static/themes/oscar/img/map";

    // init map, remove hashtag from leaflet_target name
    var map = L.map(leaflet_target);
    
    // init map view
    if(options.map_bounds) {
        // TODO hack: https://github.com/Leaflet/Leaflet/issues/2021
        setTimeout(function () {
            map.fitBounds(options.map_bounds, {
                maxZoom:17
            });
        }, 0);
    } else if (options.lon && options.lat) {
        if(options.zoom) 
            map.setView(new L.LatLng(options.lat, options.lon),options.zoom);
        else
            map.setView(new L.LatLng(options.lat, options.lon),8);
    }
    
    // TODO, better default Layer selection
	map.addLayer(options.layers.Mapnik);

	L.control.layers(options.layers).addTo(map);

    // display geojson if possible
    if(options.geojson)
        L.geoJson(options.geojson).addTo(map);
    
    return map;
};

searx.resultHoverOnBigMap = function (id) {
    if(searx.bigmap.geojsonLayerClick)
        return;

    if(searx.bigmap.geojsonLayer)
        searx.bigmap.removeLayer( searx.bigmap.geojsonLayer );
    searx.bigmap.geojsonLayer = L.geoJson(searx.bigmap.results[id].geojson).addTo(searx.bigmap);
};

searx.resultClickOnBigMap = function (id) {
    if(searx.bigmap.geojsonLayerClick) {
        searx.bigmap.removeLayer( searx.bigmap.geojsonLayerClick );
        if(searx.bigmap.geojsonLayer)
            searx.bigmap.removeLayer( searx.bigmap.geojsonLayer );
    }

    searx.bigmap.geojsonLayerClick = L.geoJson(searx.bigmap.results[id].geojson).addTo(searx.bigmap);
    
    var southWest = L.latLng(searx.bigmap.results[id].boundingbox[0], searx.bigmap.results[id].boundingbox[2]);
    var northEast = L.latLng(searx.bigmap.results[id].boundingbox[1], searx.bigmap.results[id].boundingbox[3]);

    var map_bounds = L.latLngBounds(southWest, northEast);
    // TODO hack: https://github.com/Leaflet/Leaflet/issues/2021
    setTimeout(function () {
        searx.bigmap.fitBounds(map_bounds, {
            maxZoom:17
        });
    }, 0);
};

$('#search_big_map').click(function() {
	var target_div = "#big_map_results";

	if (document.map_search.q.value === "") {
		return false;
	}

	$(target_div).html("<div id=\"result-overpass-table-loading-1\" class=\"text-center\"><img alt=\"Loading ...\" src=\"/static/themes/oscar/img/loader.gif\"></div>");
	$(target_div).removeClass('hidden');

	var search_url = "./search";

	$.ajax({
		type: "POST",
		url: search_url,
		data: {
			q: document.map_search.q_map.value,
			category_map: "on",
			format: "json",
			pageno: 1
		},

		success: function( json ) {
			if(!json || !json.results) {
				$(target_div).html("<p class=\"text-muted\">error while processing data</p>");
				return null;
			}
			
			if(!json.results.length) {
				$(target_div).html("<p class=\"text-muted\">nothing found</p>");
				return null;
			}

			newHtml = "";
			$(target_div).html("");
			
			searx.bigmap.results = [];
			for (var result in json.results) {
				singl_result = json.results[result];
				searx.bigmap.results.push(singl_result);

				newHtml += '<hr><a href="#" onClick="searx.resultClickOnBigMap(' + result + ');" onmouseover="searx.resultHoverOnBigMap(' + result + ');">' + singl_result.title + '</a>';
			}
			
			$(target_div).html(newHtml);
		},

		fail: function() {
            $(target_div).html("<p class=\"text-muted\">could not process query!</p>");
        }
	});
	
	return false;
});


$(document).ready(function(){
    // check if big map exists
    if($("#big_map").length > 0) {
        require(['leaflet-0.7.3.min'], function(leaflet) {
            searx.bigmap = searx.createLeafletMap("big_map", {
                lat: 48.13,
                lon: 13.13,
                zoom: 10
            });
        });
    }

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
            searx.createLeafletMap(leaflet_target, {
                lat: map_lat,
                lon: map_lon,
                zoom: map_zoom,
                boundingbox: map_boundingbox,
                geojson: map_geojson,
            });
        });

        // this event occour only once per element
        $( this ).off( event );
    });
});  
