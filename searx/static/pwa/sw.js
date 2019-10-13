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

// Install stage sets up the index page (home page) in the cache and opens a new cache
this.addEventListener('install', function (event) {
    console.log('[SW] Install Event processing');

    // Perform install steps
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(function (cache) {
                console.log('[SW] Installing cache ' + CACHE_NAME);
                return cache.addAll(urlsToCache)
                    .catch(function (err) {
                        console.log('[SW] Cache install Failed: ' + err);
                    });
            }).catch(function (err) {
                console.log('[SW] Install Failed: ' + err);
            })
    );
});

// If any fetch fails, it will look for the request in the cache and serve it from there first
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

// When activating the Service Worker, clear older caches
this.addEventListener('activate', function (event) {
    event.waitUntil(
        caches.keys().then(function (keys) {
            return Promise.all(keys.map(function (key) {
                clearCache(key);
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

        // If request was success, add or update it in the cache
        updateCache(event.request, res.clone());
        // TODO: figure out if the content is new and therefore the page needs a reload.

        return res;
    }).catch(function (err) {
        console.error(event.request.url, err);
        console.log('[SW] Network request Failed. Serving content from cache: ' + err);
        return fromCache(event.request);
    });
}

function handleNoCacheMatch(event) {
    return fetchFromNetworkAndCache(event);
}

function fromCache(request) {
  // Check to see if you have it in the cache
  // Return response
  // If not in the cache, then return error page
  return caches.open(CACHE_NAME).then(function (cache) {
    return cache.match(request).then(function (matching) {
      if (!matching || matching.status === 404) {
        return Promise.reject("no-match");
      }

      return matching;
    });
  });
}

function updateCache(request, response) {
    return caches.open(CACHE_NAME).then(function (cache) {
        return cache.put(request, response);
    });
}

function clearCache(key) {
    if (key !== CACHE_NAME) {
        console.log('[SW] Cleaning cache ' + key);
        return caches.delete(key);
    }
}
