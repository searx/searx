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

$(document).ready(function() {

    /**
      * focus element if class="autofocus" and id="q" is set
      */
    $('#q.autofocus').focus();


    /**
      * select all content on click if class="select-all-on-click"
      */
    $(".select-all-on-click").click(function () {
        $(this).select();
    });


    /**
      * change text during btn-collapse click if possible
      */
    $('.btn-collapse').click(function() {
        var btnTextCollapsed: string    = $(this).data('btn-text-collapsed');
        var btnTextNotCollapsed: string = $(this).data('btn-text-not-collapsed');
        
        // check if options are set
        if(btnTextCollapsed != null && btnTextNotCollapsed != null) {
            var new_html: string;
            // replace text, regarding to current state of object
            if($(this).hasClass('collapsed')) {
                new_html = $(this).html().replace(btnTextCollapsed, btnTextNotCollapsed);
            } else {
                new_html = $(this).html().replace(btnTextNotCollapsed, btnTextCollapsed);
            }
            $(this).html(new_html);
        }
    });


    /**
      * change text during btn-toggle click if possible
      */
    $('.btn-toggle .btn').click(function() {
        var btnClass: string        = 'btn-' + $(this).data('btn-class');
        var btnLabelDefault: string = $(this).data('btn-label-default');
        var btnLabelToggled: string = $(this).data('btn-label-toggled');
        
        // check if options are set
        if(btnLabelToggled != null && btnLabelDefault != null) {
            var new_html: string;
            // replace text, regarding to current state of object
            if($(this).hasClass('btn-default')) {
                new_html = $(this).html().replace(btnLabelDefault, btnLabelToggled);
            } else {
                new_html = $(this).html().replace(btnLabelToggled, btnLabelDefault);
            }
            $(this).html(new_html);
        }
        
        // toggle class of button
        if(btnClass != null) {
	        $(this).toggleClass(btnClass);
	        $(this).toggleClass('btn-default');
        }
    });
    
    /**
      * load iFrame and set src tag using data-sr
      */
    $('.media-loader').click(function() {
        var target_id: string   = $(this).data('target');
        var target: any         = $(target_id);
        var target_iframe: any  = target.find('iframe');

        // check if src is already set
        if(target_iframe.attr('src') === undefined || target_iframe.attr('src') === false) {
            // copy the attribute "data-src" to "src", to enable iframe
            target_iframe.attr('src', target_iframe.data('src'));
        }
    });


    /**
      * Select or deselect every categories on double click
      *
      * TODO: single click interferes with doubleclick event, 
      * if button was double-clicked before, and mouse wasn't removed
      * from the button for a short time
      */
    $(".btn-sm").dblclick(function() {
        // this is the class which all buttons have, if they are selected
        var btnClass: string = 'btn-' + $(this).data('btn-class');

        if($(this).hasClass('btn-default')) {
            // mark input as checked
            $(".btn-sm > input").attr('checked', 'checked');
            $(".btn-sm > input").prop("checked", true);
            
            // select bootstrap button
            $(".btn-sm").addClass(btnClass);
            $(".btn-sm").addClass('active');
            $(".btn-sm").removeClass('btn-default');
        } else {
            // mark input as not checked
            $(".btn-sm > input").attr('checked', '');
            $(".btn-sm > input").removeAttr('checked');
            $(".btn-sm > input").prop("checked", false);
            
            // unselect bootstrap button
            $(".btn-sm").removeClass(btnClass);
            $(".btn-sm").removeClass('active');
            $(".btn-sm").addClass('btn-default');
        }
    });
});