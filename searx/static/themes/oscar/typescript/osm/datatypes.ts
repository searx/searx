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

/// <reference path="../../../../typescript/jquery.d.ts" />

module searx {
    export module osm {
        export enum osmTypes {
            NODE,
            WAY,
            RELATION
        }
        
        export function getOsmTypeFromString(osmType: string): osmTypes {
            switch(osmType.toUpperCase()) {
                case 'NODE':
                    return searx.osm.osmTypes.NODE;
                case 'WAY':
                    return searx.osm.osmTypes.WAY;
                case 'RELATION':
                    return searx.osm.osmTypes.RELATION;
                default:
                    return null;
            }
        }

        export interface osmTag {
            /**
              * key of osm-attribute
              */
            key: string;
 
            /**
              * values of osm-attribute
              */
            values: string[];        
        }

        export interface osmElement {
            type: osmTypes;
            
            id: number;

            tags: osmTag[];
        }
    }
}