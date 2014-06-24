import re

# https://gitweb.torproject.org/\
# pde/https-everywhere.git/tree/4.0:/src/chrome/content/rules

# HTTPS rewrite rules
https_rules = (
    # from
    (re.compile(r'^http://(www\.|m\.|)?xkcd\.(?:com|org)/', re.I | re.U),
     # to
     r'https://\1xkcd.com/'),
    (re.compile(r'^https?://(?:ssl)?imgs\.xkcd\.com/', re.I | re.U),
     r'https://sslimgs.xkcd.com/'),
)
