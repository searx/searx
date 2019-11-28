"""searX PWA plugin - Progressive Web Application

- A2HS_
- `User Can Be Prompted To Install The Web App`_
- PWA-Checlist_

.. _A2HS:
   https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Add_to_home_screen

.._User Can Be Prompted To Install The Web App:
  https://developers.google.com/web/tools/lighthouse/audits/install-prompt

.. _PWA-Checlist:
   https://developers.google.com/web/progressive-web-apps/checklist
"""

from flask_babel import gettext

name = gettext('Progressive Web Application')
description = gettext('Allow searx to be installed on a phone almost as if it was a Native App.')
default_on = True
preference_section = 'ui'

js_dependencies = ('plugins/js/pwa.js',)
css_dependencies = ('plugins/css/pwa.css',)
