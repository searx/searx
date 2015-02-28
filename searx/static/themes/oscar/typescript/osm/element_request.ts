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
/// <reference path="datatypes.ts" />

module searx {
    export module osm {

        export function overpassApiElementRequest(osmId: number, osmType: osmTypes, options: osmElementRequestOptions): void {
            // create overpassApi request code
            var requestCode: string = "[out:json][timeout:25];(";
            switch(osmType) {
                case osmTypes.NODE:
                    requestCode += "node(" + osmId + ");";
                    break;
                case osmTypes.WAY:
                    requestCode += "way(" + osmId + ");";
                    break;
                case osmTypes.RELATION:
                    requestCode += "relation(" + osmId + ");";
                    break;
                default:
                    break;
            }
            requestCode += ");out meta;";

            // do ajax request
            $.ajax({
                type: "GET",
                // TOOD: other url?
                url: "https://overpass-api.de/api/interpreter",
                dataType: "json",
                data: {
                    data: requestCode
                }, 

                success: function(json: JSON) {
                    if(!options.success)
                        return;
 
                    // get tags
                    var resultTags: osmTag[] = [];
                    if(json['elements'].length >= 1) {
                        var tags = json['elements'][0]['tags'];
                        
                        // create key/values pairs
                        for(var tagId in tags) {
                            resultTags.push({
                                key: tagId,
                                values: tags[tagId].split(';')
                            });
                        }
                    }
                    
                    // create osmElement
                    var resultElement: osmElement = {
                        id: osmId,
                        type: osmType,
                        tags: resultTags
                    };
                    
                    // call success function
                    options.success(resultElement);
                },

                error: function() {
                    if(!options.error)
                        return;

                    // call fail function
                    options.error();
                }
            });
        }

        export interface osmElementRequestOptions {
            success? (attributes: osmElement): any;
            
            error? (): any;
        }
    }
}