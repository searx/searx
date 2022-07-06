.. SPDX-License-Identifier: AGPL-3.0-or-later

.. figure:: https://raw.githubusercontent.com/searx/searx/master/searx/static/themes/oscar/img/logo_searx_a.png
   :target: https://searx.github.io/searx/
   :alt: searX
   :width: 100%
   :align: center

-------

|searx install|
|searx homepage|
|searx wiki|
|AGPL License|
|Issues|
|commits|
|OpenCollective searx backers|
|OpenCollective searx sponsors|

Privacy-respecting, hackable `metasearch engine`_ / *pronunciation* **sɜːks**.

.. _metasearch engine: https://en.wikipedia.org/wiki/Metasearch_engine

.. |searx install| image:: https://img.shields.io/badge/-install-blue
   :target: https://searx.github.io/searx/admin/installation.html

.. |searx homepage| image:: https://img.shields.io/badge/-homepage-blue
   :target: https://searx.github.io/searx

.. |searx wiki| image:: https://img.shields.io/badge/-wiki-blue
   :target: https://github.com/searx/searx/wiki

.. |AGPL License|  image:: https://img.shields.io/badge/license-AGPL-blue.svg
   :target: https://github.com/searx/searx/blob/master/LICENSE

.. |Issues| image:: https://img.shields.io/github/issues/searx/searx?color=yellow&label=issues
   :target: https://github.com/searx/searx/issues

.. |PR| image:: https://img.shields.io/github/issues-pr-raw/searx/searx?color=yellow&label=PR
   :target: https://github.com/searx/searx/pulls

.. |commits| image:: https://img.shields.io/github/commit-activity/y/searx/searx?color=yellow&label=commits
   :target: https://github.com/searx/searx/commits/master

.. |OpenCollective searx backers| image:: https://opencollective.com/searx/backers/badge.svg
   :target: https://opencollective.com/searx#backer

.. |OpenCollective searx sponsors| image:: https://opencollective.com/searx/sponsors/badge.svg
   :target: https://opencollective.com/searx#sponsor


If you are looking for running instances, ready to use, then visit searx.space_.

Otherwise jump to the user_, admin_ and developer_ handbooks you will find on
our homepage_.

.. _searx.space: https://searx.space
.. _user: https://searx.github.io/searx/user
.. _admin: https://searx.github.io/searx/admin
.. _developer: https://searx.github.io/searx/dev
.. _homepage: https://searx.github.io/searx

contact:
  openhub_ // twitter_ // IRC: #searx @ Libera (irc.libera.chat)

.. _openhub: https://www.openhub.net/p/searx
.. _twitter: https://twitter.com/Searx_engine

**************************
Frequently asked questions
**************************

Is searx in maintenance mode?
#############################

No, searx is accepting new features, including new engines. We are also adding
engine fixes or other bug fixes when needed. Also, keep in mind that searx is
maintained by volunteers who work in their free time. So some changes might take
some time to be merged.

We reject features that might violate the privacy of users. If you really want
such a feature, it must be disabled by default and warn users about the consequances
of turning it off.

What is the difference between searx and SearxNG?
#################################################

TL;DR: If you want to run a public instance, go with SearxNG. If you want to
self host your own instance, choose searx.

SearxNG is a fork of searx, created by a former maintainer of searx. The fork
was created because the majority of the maintainers at the time did not find
the new proposed features privacy respecting enough. The most significant issue is with
engine metrics.

Searx is built for privacy conscious users. It comes a unique set of
challanges. One of the problems we face is that users rather not report bugs,
because they do not want to publicly share what engines they use or what search
query triggered a problem. It is a challenge we accepted.

The new metrics feature collects more information to make engine maintenance easier.
We could have had better and more error reports to benefit searx maintainers.
However, we believe that the users of searx must come first, not the
software. We are willing to compromise on the lack of issue reports to avoid
violating the privacy of users.

Furthermore, SearxNG is under heavy refactoring and dependencies are constantly updated, even
if it is unnecessary. It increases the risk of introducing regressions. In searx
we strive for stability, rather than moving fast and breaking things.

Is searx for me?
################

Are you privacy conscious user? Then yes.

In searx we decided to double down on being privacy respecting. We are picking
engine changes from SearxNG, but we are not implementing engine detailed
monitoring and not adding a new UI that relies on Javascript.

If you are willing to give up some privacy respecting features, we encourage you to
adopt SearxNG. Searx is targeted for privacy conscious users who run their
instances locally, instead of using public instances.

Why should I use SearxNG?
#########################

SearxNG has rolling releases, depencencies updated more frequently, and engines are fixed
faster. It is easy to set up your own public instance, and monitor its
perfomance and metrics. It is simple to maintain as an instance adminstrator.

As a user, it provides a prettier user interface and nicer experience.
