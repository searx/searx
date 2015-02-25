if(searx.autocompleter) {
    window.addEvent('domready', function() {
	    new Autocompleter.Request.JSON('q', './autocompleter', {
		    postVar:'q',
		    postData:{
			    'format': 'json'
		    },
		    ajaxOptions:{
		        timeout: 5   // Correct option?
		    },
		    'minLength': 4,
		    'selectMode': false,
		    cache: true,
		    delay: 300
	    });
    });
}

(function (w, d) {
    'use strict';
    function addListener(el, type, fn) {
        if (el.addEventListener) {
            el.addEventListener(type, fn, false);
        } else {
            el.attachEvent('on' + type, fn);
        }
    }

    function placeCursorAtEnd() {
        if (this.setSelectionRange) {
            var len = this.value.length * 2;
            this.setSelectionRange(len, len);
        }
    }

    addListener(w, 'load', function () {
        var qinput = d.getElementById('q');
        if (qinput !== null && qinput.value === "") {
            addListener(qinput, 'focus', placeCursorAtEnd);
            qinput.focus();
        }
    });

    if (!!('ontouchstart' in window)) {
        document.getElementsByTagName("html")[0].className += " touch";
    }

})(window, document);

