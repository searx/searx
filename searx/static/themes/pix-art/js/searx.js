if(searx.autocompleter) {
    window.addEvent('domready', function() {
	    new Autocompleter.Request.JSON('q', '/autocompleter', {
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

var xmlHttp

function GetXmlHttpObject(){

    var xmlHttp = null;

    try {
        // Firefox, Opera 8.0+, Safari
        xmlHttp = new XMLHttpRequest();
    }
    catch (e) {
        // Internet Explorer
        try {
            xmlHttp = new ActiveXObject("Msxml2.XMLHTTP");
        }
        catch (e){
            xmlHttp = new ActiveXObject("Microsoft.XMLHTTP");
        }
    }
    return xmlHttp;
}

var timer;

// Load more results
function load_more(query,page){

    xmlHttp = GetXmlHttpObject();
    clearTimeout(timer);

    if(xmlHttp == null){
        alert ("Your browser does not support AJAX!");
        return;
    }

    favicons[page] = [];

    xmlHttp.onreadystatechange = function(){
        
        var loader = document.getElementById('load_more');

        // If 4, response OK
        if (xmlHttp.readyState == 4){
            
            var res = xmlHttp.responseText;

            clearTimeout(timer);
            timer = setTimeout(function(){},6000);

            var results = document.getElementById('results_list');

            var newNode = document.createElement('span');      
            newNode.innerHTML = res;
            results_list.appendChild(newNode);

            var scripts = newNode.getElementsByTagName('script');
            for (var ix = 0; ix < scripts.length; ix++) {
                eval(scripts[ix].text);
            }

            load_images(page);
            document.getElementById("load_more").onclick = function() { load_more(query, (page+1)); }
            loader.removeAttribute("disabled");
            
        } else {
            loader.disabled = 'disabled';
        }
    }
    var url = "/";
    var params = "q="+query+"&pageno="+page+"&category_general=1&category_files=1&category_images=1&category_it=1&category_map=1&category_music=1&category_news=1&category_social+media=1&category_videos=1";
    xmlHttp.open("POST",url,true);
    xmlHttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xmlHttp.setRequestHeader("Content-length", params.length);
    xmlHttp.setRequestHeader("Connection", "close");
    xmlHttp.send(params);
}

// Load the images on the canvas in the page
function load_images(page){
    var arrayLength = favicons[page].length;
    for (var i = 1; i < arrayLength+1; i++) {
        var img = new Image();
        img.setAttribute("i",i)
        img.onload = function () {
            var id = 'canvas-'+page+'-'+this.getAttribute("i");
            var can = document.getElementById(id);
            var ctx = can.getContext("2d");
            ctx.drawImage(this, 0, 0, 16, 16);
        };
        img.src = favicons[page][i];
    }
}