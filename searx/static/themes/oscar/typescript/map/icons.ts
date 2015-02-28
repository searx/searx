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

module searx {
    export module map {
        export module icons {

            export function getMarkerIcon(): L.Icon {
	            return L.icon({
					iconUrl: './static/img/map/marker-icon.png',
					shadowUrl: './static/img/map/marker-shadow.png',
					iconSize: new L.Point(25, 41),
					iconAnchor: new L.Point(12, 41),
					shadowSize: new L.Point(41, 41),
					shadowAnchor: new L.Point(12, 41)
				});
			}
			
			export function getMarkerIconGreen(): L.Icon {
                return L.icon({
                    iconUrl: './static/img/map/marker-icon-green.png',
                    shadowUrl: './static/img/map/marker-shadow.png',
                    iconSize: new L.Point(25, 41),
                    iconAnchor: new L.Point(12, 41),
                    shadowSize: new L.Point(41, 41),
                    shadowAnchor: new L.Point(12, 41)
                });
            }
        }
    }
}