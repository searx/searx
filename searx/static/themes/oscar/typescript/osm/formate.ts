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

/// <reference path="datatypes.ts" />

module searx {
    export module osm {
        export function formateValues(tag: osmTag): string[] {
            var returnParts: string[] = [];
        
            for(var id in tag.values) {
                switch(tag.key) {
	                case "phone":
	                case "fax":
	                    returnParts.push("<a href=\"tel:" + tag.values[id].replace(/ /g,'') + "\">" + tag.values[id] + "</a>");
	                    break;
	                case "email":
                        returnParts.push("<a href=\"mailto:" + tag.values[id] + "\">" + tag.values[id] + "</a>");
                        break;
                    case "website":
                    case "url":
                        var weburl: string = tag.values[id];
                        // set http protocol if nothing is set
                        if(!/^\w+:\/\//.test(weburl))
                            weburl = "http://" + weburl;
                        returnParts.push("<a href=\"" + weburl + "\">" + tag.values[id] + "</a>");
                        break;
                    case "wikidata":
                        returnParts.push("<a href=\"https://www.wikidata.org/wiki/" + tag.values[id] + "\">" + tag.values[id] + "</a>");
                        break;
                    case "wikipedia":
                        // check if language-code is set
                        if(tag.values[id].indexOf(":") != -1) {
                            returnParts.push("<a href=\"https://" + tag.values[id].substring(0,tag.values[id].indexOf(":")) + 
                                ".wikipedia.org/wiki/" + tag.values[id].substring(tag.values[id].indexOf(":")+1) + "\">" +
                                tag.values[id] + "</a>");
                        }
                        break;
	                default:
	                    returnParts.push(tag.values[id]);
	                    break;
	            }
            }
            
            return returnParts;
        }
    }
}