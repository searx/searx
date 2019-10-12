// Service Worker

var CACHE_NAME = 'searx-cache-v1';

var urlsToCache = [
    '/',
    '/static/pwa/sw.js',
    '/static/css/bootstrap.min.css',
    // TODO If possible, and compatible with PWA, make this list dynamic
    // or put in cache all default themes css and js for quick theme switch
    '/static/js/jquery-1.11.1.min.js',
    '/static/js/bootstrap.min.js',
    '/static/js/require-2.1.15.min.js',
    '/static/js/searx.min.js',
    '/static/js/require-2.1.15.min.js'
];


this.addEventListener('install', function (event) {
    // Perform install steps
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(function (cache) {
                console.log('Installing cache ' + CACHE_NAME);
                return cache.addAll(urlsToCache);
            })
    );
});

this.addEventListener('fetch', function (event) {
    event.respondWith(
        caches.match(event.request)
            .then(function (response) {
                if (!response) {
                    return handleNoCacheMatch(event);
                }
                // Update cache record in the background
                fetchFromNetworkAndCache(event);
                // Reply with stale data
                return response
            })
    );
});

this.addEventListener('activate', function (event) {
    event.waitUntil(
        caches.keys().then(function (keys) {
            return Promise.all(keys.map(function (key) {
                if (key !== CACHE_NAME) {
                    console.log('Cleaning cache ' + key);
                    return caches.delete(key);
                }
            }));
        }));
});


function fetchFromNetworkAndCache(event) {
    // DevTools opening will trigger these o-i-c requests, which this SW can't handle.
    // There's probaly more going on here, but I'd rather just ignore this problem. :)
    // https://github.com/paulirish/caltrainschedule.io/issues/49
    if (event.request.cache === 'only-if-cached' && event.request.mode !== 'same-origin') {
        return;
    }

    return fetch(event.request).then(res => {
        // foreign requests may be res.type === 'opaque' and missing a url
        if (!res.url) {
            return res;
        }
        // Only cache GET requests
        if (event.request.method !== 'GET') {
            return res;
        }
        // regardless, we don't want to cache other origin's assets
        if (new URL(res.url).origin !== location.origin) {
            return res;
        }

        return caches.open(CACHE_NAME).then(function (cache) {
            // TODO: figure out if the content is new and therefore the page needs a reload.
            cache.put(event.request, res.clone());
            return res;
        });
    }).catch(function (err) {
        console.error(event.request.url, err);
    });
}

function handleNoCacheMatch(event) {
    return fetchFromNetworkAndCache(event);
}
