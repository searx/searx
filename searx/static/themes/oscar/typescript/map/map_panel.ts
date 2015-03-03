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
    export module map {
        /**
          * show ui-panel with the given class
          *
          * @param map_ui reference to main map_ui div
          * @param panel_name name of panel which has to be activated
          */
        export function showPanelUi(map_ui: JQuery, panel_name: string): void {
            // show only the map_ui and the given children
            map_ui.children('.panel-default').css('display', 'none');
            map_ui.children('.' + panel_name).css('display', 'block');
            map_ui.css('display', 'block');
        }
        
        /**
          * hide ui-panel
          *
          * @param map_ui reference to main map_ui div
          */
        export function hidePanelUi(map_ui: JQuery): void {
            // hide map_ui and all children panel
            map_ui.css('display', 'none');
            map_ui.children('.panel-default').css('display', 'none');
        }
        
        /**
          * toggle ui-panel with the given class
          *
          * @param map_ui reference to main map_ui div
          * @param panel_name name of panel which has to be toggled
          *
          * @return true if panel is activated, false if it is deactivated
          */
        export function togglePanelUi(map_ui: JQuery, panel_name: string): boolean {
            // check if panel is currently visible
            if(map_ui.css('display') == 'none' || map_ui.children('.' + panel_name).css('display') == 'none') {
                // if not, show panel
                showPanelUi(map_ui, panel_name);
                return true;
            } else {
                // otherwise hide panel
                hidePanelUi(map_ui);
                return false;
            }
        }
    }
}