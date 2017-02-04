import string
from requests import get
from flask_babel import gettext
from searx import settings

# Required answerer attribute
# Specifies which search query keywords triggers this answerer
keywords = ('myip',)

# Returns a string with all the information retrieved from ip-api.com's API
def get_answer():
    # Find the outgoing proxies settings from the user configuration.
    outgoing_proxies = settings['outgoing'].get('proxies', None)
	
    # Initiate a GET request and set the outgoing proxies, if any were set in
    # settings.yml.
    ip_info = get('http://ip-api.com/json', proxies=outgoing_proxies).json()

    # Return the formatted string.
    return "Your IP is %s from %s, %s, provided by %s" % (
        ip_info['query'],
        ip_info['city'],
        ip_info['country'],
        ip_info['isp'])

# Required answerer function
def answer(query):
    try:
        return [{'answer': get_answer()}]
    except:
        return []

# Required answerer function
def self_info():
    return {'name': gettext('Your Public/External IP Address'),
            'description': gettext('Get your public IP and information'),
            'examples': [u'myip']}
