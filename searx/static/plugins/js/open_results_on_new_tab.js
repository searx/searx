$(document).ready(function() {
    // Only add target=_blank when cookie is present (setting) and set to 1
    let matchingCookies = document.cookie.split(' ').filter(e => e.startsWith('results_on_new_tab='));
    if(matchingCookies.length == 1) {
      let resultsOnNewTab = parseInt(matchingCookies[0].split('=')[1]);

      if(resultsOnNewTab)
        $('.result_header > a').attr('target', '_blank');
    }
});
