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
* (C) 2017 by Alexandre Flament, <alex@al-f.net>
*/
(function (w, d, searx) {
  'use strict';

  searx.ready(function () {
    searx.on('.searx_overpass_request', 'click', function(event) {
      // no more request
      this.classList.remove("searx_overpass_request");

      //
      var overpass_url = "https://overpass-api.de/api/interpreter?data=";
      var query_start = overpass_url + "[out:json][timeout:25];(";
      var query_end = ");out meta;";

      var osm_id = this.dataset.osmId;
      var osm_type = this.dataset.osmType;
      var result_table = d.querySelector("#" + this.dataset.resultTable);
      var result_table_loadicon = d.querySelector("#" + this.dataset.resultTableLoadicon);

      // tags which can be ignored
      var osm_ignore_tags = [ "addr:city", "addr:country", "addr:housenumber", "addr:postcode", "addr:street" ];

      if(osm_id && osm_type && result_table) {
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
          // console.log(query);
          searx.http( 'GET', query ).then(function(html, contentType) {
            html = JSON.parse(html);
            if(html && html.elements && html.elements[0]) {
              var element = html.elements[0];
              var newHtml = "";
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
              result_table_loadicon.classList.add('invisible');
              result_table.classList.remove('invisible');
              result_table.querySelector("tbody").innerHTML = newHtml;
            }
          })
          .catch(function() {
            result_table_loadicon.innerHTML = result_table_loadicon.innerHTML + "<p class=\"text-muted\">could not load data!</p>";
          });
        }
      }

      // this event occour only once per element
      event.preventDefault();
    });

    searx.on('.searx_init_map', 'click', function(event) {
      // no more request
      this.classList.remove("searx_init_map");

      //
      var leaflet_target = this.dataset.leafletTarget;
      var map_lon = parseFloat(this.dataset.mapLon);
      var map_lat = parseFloat(this.dataset.mapLat);
      var map_zoom = parseFloat(this.dataset.mapZoom);
      var map_boundingbox = JSON.parse(this.dataset.mapBoundingbox);
      var map_geojson = JSON.parse(this.dataset.mapGeojson);

      searx.loadStyle('leaflet/leaflet.css');
      searx.loadScript('leaflet/leaflet.js', function() {
        var map_bounds = null;
        if(map_boundingbox) {
          var southWest = L.latLng(map_boundingbox[0], map_boundingbox[2]);
          var northEast = L.latLng(map_boundingbox[1], map_boundingbox[3]);
          map_bounds = L.latLngBounds(southWest, northEast);
        }

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
          // Still useful ?
          setTimeout(function () {
            map.fitBounds(map_bounds, {
              maxZoom:17
            });
          }, 0);
        } else if (map_lon && map_lat) {
          if(map_zoom) {
            map.setView(new L.latLng(map_lat, map_lon),map_zoom);
          } else {
            map.setView(new L.latLng(map_lat, map_lon),8);
          }
        }

        map.addLayer(osmMapnik);

        var baseLayers = {
          "OSM Mapnik": osmMapnik/*,
          "OSM Wikimedia": osmWikimedia*/
        };

        L.control.layers(baseLayers).addTo(map);

        if(map_geojson) {
          L.geoJson(map_geojson).addTo(map);
        } /*else if(map_bounds) {
          L.rectangle(map_bounds, {color: "#ff7800", weight: 3, fill:false}).addTo(map);
        }*/
      });

      // this event occour only once per element
      event.preventDefault();
    });
  });
})(window, document, window.searx);
