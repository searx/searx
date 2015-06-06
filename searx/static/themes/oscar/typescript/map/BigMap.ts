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
/// <reference path="../../../../typescript/bootstrap.d.ts" />
/// <reference path="../oscar.d.ts" />
/// <reference path="../autocompleter.ts" />
/// <reference path="../osm/element_request.ts" />
/// <reference path="../osm/datatypes.ts" />
/// <reference path="Map.ts" />
/// <reference path="map_panel.ts" />
/// <reference path="icons.ts" />

module searx {
    export module map {
        export class BigMap extends Map {
            public search_results: BigMapResult[];
            public active_result: BigMapResult;

            constructor(mapId: string, options?: MapOptions) {
                super(mapId, options);
                this.initSidebar();
                this.active_result = null;
            }
            
            initSidebar() {
                var thisHelp: BigMap = this;
		        // check if autocompleter is activated, and searchfield is present
		        // TODO: some styling issues
		        if(searx.options.autocompleter && $('#q_map').length > 0) {
		            // create autocompleter
		            $('#q_map').typeahead({
		                hint: true,
		                highlight: true,
		                minLength: 1 
		            },{
		                name: 'search-results',
		                displayKey: function(result: any): string {
		                    return result;
		                },
		                source: searx.getNewAutocompleter('#q_map').ttAdapter()
		            });
		        }
		        
	            $('#search_big_map').click(function() {
		            var target_div = $('#map-sidebar').children('.results-sidebar');
		            if ($('#q_map').val() === "") {
		               return false;
		            }
		            
		            // close autocompleter suggestions
		            $('#q_map').typeahead('close');
		            
		            searx.map.expandSidebar($('#map-sidebar'));
		            searx.map.showLoadingIcon(target_div);
		            target_div.children('.no-results').css('display', 'none');
		            var result_div: JQuery = target_div.children('.big-map-results').html("");
		
		            var search_url = "./search";
		           
		            $.ajax({
		                type: "POST",
		                url: search_url,
		                data: {
		                q: $('#q_map').val(),
		                category_map: "on",
		                format: "json",
		                pageno: 1
		                },
		                success: function( json ) {
		                    if(!json || !json.results) {
		                       target_div.find('.error_text')
		                            .css('display', 'block')
		                            .html('error while processing data!');
		                       return null;
		                    }
		                    
		                    searx.map.hideLoadingIcon(target_div);
		                    if(!json.results.length) {
		                       target_div.children('.no-results').css('display', 'block');
		                       return null;
		                    }
		                    
		                    this.search_results = json.results;
		                    
		                    for (var result in this.search_results) {
		                       thisHelp.addResultToSidebar(this.search_results[result], result_div, result);
		                    }
		                },
		                error: function() {
		                    target_div.find('.error_text')
		                            .css('display', 'block')
		                            .html('could not process query!');
		                }
		            });
		
		            return false;
		        });
		        
		        // close panel if close button is clicked
		        $('#map-sidebar').children('.results-sidebar').find('.close').click(function() {
		            searx.map.reduceSidebar($('#map-sidebar'))
		            thisHelp.setResult(null);
		            // don't reload the page
		            return false;
		        });
            }

            addResultToSidebar(search_result: any, result_div: JQuery, result_id: number) {
                var thisMap: L.Map = this.map;
                var thisHelp: BigMap = this;
                
                var re = new RegExp("(" + $('#q_map').val() + ")","gi");
                var title: string = search_result.title.replace(re, "<span class=\"highlight\">$1</span>")
                
                if(search_result.address && search_result.address.name)
                    title = search_result.address.name.replace(re, "<span class=\"highlight\">$1</span>")
                
                var result: JQuery = $(document.createElement('h4'))
                    .html(title)
                    .addClass('cursor-pointer')
                    .addClass('result_header')
                    .addClass('map-result-title')
                    //.attr('data-toggle','collapse')
                    //.attr('data-parent','#big-map-results')
                    .attr('data-target','#big-map-result-'+result_id)
                    .click(function() {
                        //L.marker(new L.LatLng(search_result.latitude, search_result.longitude), {icon: icons.getMarkerIcon()}).addTo(thisMap);
                        thisHelp.setResult(new BigMapResult(thisMap, search_result));
                        $(this).parent().children('p').each(function( index ) {
                            // we have to hide all children manually because the script doesn't work correctly
                            if($(this).attr('id') != 'big-map-result-'+result_id) {
                                $(this).collapse('hide');
                            } else {
                                $(this).collapse('show');
                            }
                        });
                    });
                result_div.append(result);
                
                
                // create result html
                var result_html: string = '';
                if(search_result.address) {
	                if(search_result.address.name)
	                    result_html += '<strong itemprop="name">' + search_result.address.name + '</strong><br/>';
	                if(search_result.address.road) {
	                    result_html += '<span itemprop="streetAddress">';
	                    if(search_result.address.house_number)
	                        result_html += search_result.address.house_number + ', ';
	                    result_html += search_result.address.road + '</span><br/>';
	                }
	                if(search_result.address.locality) {
	                    result_html += '<span itemprop="addressLocality">' + search_result.address.locality + '</span>';
	                    if(search_result.address.postcode)
	                        result_html += ', <span itemprop="postalCode">' + search_result.address.postcode + '</span>';
	                    result_html += '<br/>';
	                }
	                if(search_result.address.country) 
	                    result_html += '<span itemprop="addressCountry">' + search_result.address.country + '</span>';
	           }
	           result_html += '<p class="text-muted" style="padding-top: 10px;"><a class="text-muted" href="' + search_result.url + '">' + search_result.url + '</p>';

	           var informations: JQuery = $(document.createElement('p'))
	               .html(result_html)
	               .addClass('collapse')
	               .collapse({toggle: false})
	               .attr('id', 'big-map-result-'+result_id);
	           result_div.append(informations);  
            }
            
            setResult(new_active_result: BigMapResult) {
                if(this.active_result != null)
                    this.active_result.removeFromMap();
                if(new_active_result != null)
                    new_active_result.addToMap();
                this.active_result = new_active_result;
            }
        }
        
        export class BigMapResult {
            _map: L.Map;
            _result: any;
            _result_layer: L.ILayer;
            
            constructor(map: L.Map, result: any) {
                this._map = map;
                this._result = result;
            }
            
            addToMap() {
                if(this._result.geojson) {
                    this._result_layer = L.geoJson(this._result.geojson).addTo(this._map);
                } else {
                    this._result_layer = L.marker(new L.LatLng(this._result.latitude, this._result.longitude), {icon: icons.getMarkerIcon()}).addTo(this._map);
                }
                
                // set default-view of map
                if(this._result.boundingbox) {
                    var target_boundingbox: L.LatLngBounds = L.latLngBounds(
	                    L.latLng(
	                        this._result.boundingbox[0], 
	                        this._result.boundingbox[2]
	                    ),
	                    L.latLng(
	                        this._result.boundingbox[1], 
	                        this._result.boundingbox[3]
	                    )
	                );
	                // set boundingbox if possible
	                var map: L.Map = this._map;
	                // TODO hack: https://github.com/Leaflet/Leaflet/issues/2021
	                setTimeout(function(){
	                        map.fitBounds(target_boundingbox, {
	                            maxZoom: 17
	                        });
	                }, 0);
                } else if(this._result.latitude) {
                    // otherwise using lat-lng if possible
                    if(this._result.zoom) 
                        this._map.setView(new L.LatLng(this._result.latitude, this._result.longitude), this._result.zoom);
                    else
                        this._map.setView(new L.LatLng(this._result.latitude, this._result.longitude), 8);
                }
            }
            
            removeFromMap() {
                this._map.removeLayer(this._result_layer);
            }
        }
    }
}