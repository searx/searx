===========================
Why use a private instance?
===========================

  *"Is it worth to run my own instance?"*

\.\. is a common question among searx users.  Before answering this question,
see what options a searx user has.

Public instances are open to everyone who has access to its URL.  Usually, these
are operated by unknown parties (from the users' point of view).  Private
instances can be used by a select group of people.  It is for example a searx of
group of friends or a company which can be accessed through VPN.  Also it can be
single user one which runs on the user's laptop.

To gain more insight on how these instances work let's dive into how searx
protects its users.

How does searx protect privacy?
===============================

Searx protects the privacy of its users in multiple ways regardless of the type
of the instance (private, public).  Removal of private data from search requests
comes in three forms:

 1. removal of private data from requests going to search services
 2. not forwarding anything from a third party services through search services
    (e.g. advertisement)
 3. removal of private data from requests going to the result pages

Removing private data means not sending cookies to external search engines and
generating a random browser profile for every request.  Thus, it does not matter
if a public or private instance handles the request, because it is anonymized in
both cases.  IP addresses will be the IP of the instance.  But searx can be
configured to use proxy or Tor.  `Result proxy
<https://github.com/asciimoo/morty>`__ is supported, too.

Searx does not serve ads or tracking content unlike most search services.  So
private data is not forwarded to third parties who might monetize it.  Besides
protecting users from search services, both referring page and search query are
hidden from visited result pages.


What are the consequences of using public instances?
----------------------------------------------------

If someone uses a public instance, they have to trust the administrator of that
instance.  This means that the user of the public instance does not know whether
their requests are logged, aggregated and sent or sold to a third party.

Also, public instances without proper protection are more vulnerable to abusing
the search service, In this case the external service in exchange returns
CAPTCHAs or bans the IP of the instance.  Thus, search requests return less
results.

I see. What about private instances?
------------------------------------

If users run their own instances, everything is in their control: the source
code, logging settings and private data.  Unknown instance administrators do not
have to be trusted.

Furthermore, as the default settings of their instance is editable, there is no
need to use cookies to tailor searx to their needs.  So preferences will not be
reset to defaults when clearing browser cookies.  As settings are stored on
their computer, it will not be accessible to others as long as their computer is
not compromised.

Conclusion
==========

Always use an instance which is operated by people you trust.  The privacy
features of searx are available to users no matter what kind of instance they
use.

If someone is on the go or just wants to try searx for the first time public
instances are the best choices.  Additionally, public instance are making a
world a better place, because those who cannot or do not want to run an
instance, have access to a privacy respecting search service.
