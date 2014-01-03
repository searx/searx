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

})(window, document);

