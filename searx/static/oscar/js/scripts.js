/**
 _                 _       _                  
| |__   ___   ___ | |_ ___| |_ _ __ __ ___  __
| '_ \ / _ \ / _ \| __/ __| __| '__/ _` \ \/ /
| |_) | (_) | (_) | |_\__ | |_| | | (_| |>  < 
|_.__/ \___/ \___/ \__|___/\__|_|  \__,_/_/\_\.js

*/

requirejs.config({
baseUrl: '/static/oscar/js',
paths: {
app: '../app'
}
});

if(searx.autocompleter) {
    searx.searchResults = new Bloodhound({
        datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        remote: '/autocompleter?q=%QUERY'
    });
    searx.searchResults.initialize();
}

$(document).ready(function(){
    $('.btn-toggle .btn').click(function() {
        var btnClass = 'btn-' + $(this).data('btn-class');
        var btnLabelDefault = $(this).data('btn-label-default');
        var btnLabelToggled = $(this).data('btn-label-toggled');
        if(btnLabelToggled != '') {
            if($(this).hasClass('btn-default')) {
                
                var html = $(this).html().replace(btnLabelDefault, btnLabelToggled);
            } else {
                var html = $(this).html().replace(btnLabelToggled, btnLabelDefault);
            }
            $(this).html(html);
        }
        $(this).toggleClass(btnClass);
        $(this).toggleClass('btn-default');
    });

    $('.btn-collapse').click(function() {
        var btnTextCollapsed = $(this).data('btn-text-collapsed');
        var btnTextNotCollapsed = $(this).data('btn-text-not-collapsed');
        
        if(btnTextCollapsed != '' && btnTextNotCollapsed != '') {
            if($(this).hasClass('collapsed')) {
                var html = $(this).html().replace(btnTextCollapsed, btnTextNotCollapsed);
            } else {
                var html = $(this).html().replace(btnTextNotCollapsed, btnTextCollapsed);
            }
            $(this).html(html);
        }
    });
    
    $(".select-all-on-click").click(function () {
        $(this).select();
    });
    
    if(searx.autocompleter) {
        $('#q').typeahead(null, {
            name: 'search-results',
            displayKey: function(result) {
                return result;
            },
            source: searx.searchResults.ttAdapter()
        });
    }

    $(".searx_init_map").on( "click", function( event ) {
        var leaflet_target = $(this).data('leaflet-target');
        var map_lon = $(this).data('map-lon');
        var map_lat = $(this).data('map-lat');
        var map_zoom = $(this).data('map-zoom');
        var map_boundingbox = $(this).data('map-boundingbox');
        var map_geojson = $(this).data('map-geojson');
  
        require(['leaflet-0.7.3.min'], function(leaflet) {
            if(map_boundingbox) {
                var southWest = L.latLng(map_boundingbox[0], map_boundingbox[2]),
                    northEast = L.latLng(map_boundingbox[1], map_boundingbox[3]),
                    map_bounds = L.latLngBounds(southWest, northEast);
            }

            // TODO hack
            // change default imagePath
            L.Icon.Default.imagePath = 	"/static/oscar/img/map";

            // init map
            var map = L.map(leaflet_target);

            // create the tile layer with correct attribution
	        var osmUrl='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
	        var osmAttrib='Map data © <a href="https://openstreetmap.org">OpenStreetMap</a> contributors';
	        var osm = new L.TileLayer(osmUrl, {minZoom: 1, maxZoom: 19, attribution: osmAttrib});		

            // init map view
            if(map_bounds) {
                // TODO hack: https://github.com/Leaflet/Leaflet/issues/2021
                setTimeout(function () {
                    map.fitBounds(map_bounds);
                }, 0);
            } else if (map_lon && map_lat) {
                if(map_zoom) 
                    map.setView(new L.LatLng(map_lat, map_lon),map_zoom);
                else
                    map.setView(new L.LatLng(map_lat, map_lon),8);
            }

	        map.addLayer(osm);

            if(map_geojson)
                L.geoJson(map_geojson).addTo(map);
	        //if(map_bounds)
	        //    L.rectangle(map_bounds, {color: "#ff7800", weight: 3, fill:false}).addTo(map);
        });

        // this event occour only once per element
        $( this ).off( event );
    });
});  
