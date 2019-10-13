
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function () {
        if (navigator.serviceWorker.controller) {
            console.log('[PWA] ServiceWorker found, no need to register');
        } else {
            navigator.serviceWorker.register('/static/pwa/sw.js', {
                scope: './'
              }).then(function (registration) {
                // Registration was successful
                console.log('[PWA] ServiceWorker registration successful with scope: ' + registration.scope);
            }, function (err) {
                // registration failed :(
                console.log('[PWA] ServiceWorker registration failed: ', err);
            });
        }
    });

    let installPromptEvent = null;
    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        installPromptEvent = e;

        console.log('[PWA] Searx could be installed');
        showAddToHomeScreen();
    });

    function showAddToHomeScreen(event) {
        btnAdd = document.getElementById('pwa-install-link');

        if (installPromptEvent === null) {
            console.log('[PWA] No A2HS event stored for this device');
        } else if (btnAdd === null) {
            console.log('[PWA] The page has not finished initializing. Postponing A2HS on page load.');
            document.body.addEventListener('load', showAddToHomeScreen);
        } else {
            // Update UI to notify the user they can add to home screen
            btnAdd.style.display = 'block';

            btnAdd.addEventListener('click', addToHomeScreen);
        }
    }

    function addToHomeScreen(event) {
        // Show the prompt
        hideAddToHomeScreen();

        if (installPromptEvent === null) {
            console.log('[PWA] No A2HS event to trigger for this device');
        } else {
            installPromptEvent.prompt();

            // Wait for the user to respond to the prompt
            installPromptEvent.userChoice
                .then((choiceResult) => {
                    if (choiceResult.outcome === 'accepted') {
                        console.log('[PWA] User accepted the A2HS prompt');
                    } else {
                        console.log('[PWA] User dismissed the A2HS prompt');
                    }
                    installPromptEvent = null;
                });
        }
    }

    function hideAddToHomeScreen(event) {
        btnAdd = document.getElementById('pwa-install-link');

        // hide our user interface that shows our A2HS button
        if (btnAdd !== null) {
            btnAdd.style.display = 'none';
        }
    }

    window.addEventListener('appinstalled', hideAddToHomeScreen);

}
