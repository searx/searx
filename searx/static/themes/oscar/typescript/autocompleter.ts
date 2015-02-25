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
/// <reference path="../../../typescript/typeahead.d.ts" />
/// <reference path="oscar.d.ts" />

module searx {

    /**
      * Create a new Autocompleter Object which can be used by typeahead
      *
      * @param inputId Id of the input field, to fetch current value (for example: '#q')
      *
      * @return a initialized Bloodhound object
      */
    export function getNewAutocompleter(inputId: string): any {
        var remote_options: Bloodhound.RemoteOptions<any>;
        var remote_url = './autocompleter';

        if(searx.options.method.toUpperCase() == "POST") {
            // do autocompletion using POST request
            remote_options = {
                url: remote_url,
                replace: function(url, query) {
                    return url + "#" + query;
                },
                ajax : {
                    data: {
                        q: function() {
                            // fetch current query from input field
                            return $(inputId).val()
                        }
                    },
                    type: "POST"
                }
            };
        } else {
            // do autocompletion using GET request
            remote_options = {
                url: remote_url + '?q=%QUERY'
            };
        }
    
        var new_autocompleter = new Bloodhound({
            datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
            queryTokenizer: Bloodhound.tokenizers.whitespace,
            remote: remote_options
        });
        
        new_autocompleter.initialize();
        
        return new_autocompleter;
    }
}

$(document).ready(function() {
    // check if autocompleter is activated, and searchfield is present
    if(searx.options.autocompleter && $('#q').length > 0) {
        // create autocompleter
        $('#q').typeahead({
            hint: true,
            highlight: true,
            minLength: 1 
        },{
            name: 'search-results',
            displayKey: function(result: any): string {
                return result;
            },
            source: searx.getNewAutocompleter('#q').ttAdapter()
        });
    }
});
