.. _public instances:

..
   links has been ported from markdown to reST by::

      regexpr:        \[([^\]]*)\]\(([^)]*)\)
      substitution:  `\1 <\2>`__


======================
Public Searx instances
======================

.. _mailing list: mailto:searx-instances@autistici.org
.. _subscription page: https://www.autistici.org/mailman/listinfo/searx-instances


Useful information
==================

* Up-to-date health report available on https://stats.searx.xyz [1]_, for onion
  (tor) services: https://stats.searx.xyz/tor.html

* Searx instances `mailing list`_ & `subscription page`_.

* Some of the Searx instances have a CAcert SSL certificate. You can install the
  missing root cert `from here <http://www.cacert.org/index.php?id=3>`__.

* To add your own Searx instance to this page send us your PR.  A GitHub account
  is required to send PR or add an issue.

.. [1] Note that most of the instances with a A+ grade in CSP column in this
       site are not fully functional - for example auto-completion may not work.


List of public Searx instances
==============================

Meta-searx instances
====================

These are websites that source from other searx instances.  These are useful if
you can't decide which Searx instance to use:


.. flat-table:: Meta-searx instances
   :header-rows: 1
   :stub-columns: 0
   :widths: 2 1 2 4 4

   * - clearnet host
     - onion host
     - issuer
     - source selection method
     - extra privacy features

   * - `Neocities <https://searx.neocities.org/>`__
     - n/a
     - Comodo (`Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.neocities.org>`__)
     - Redirects users directly to a random selection of any known running
       server after entering query. Requires
       Javascript. `Changelog <https://searx.neocities.org/changelog.html>`__.
     - Excludes servers with user tracking and analytics or are proxied through
       Cloudflare.

   * - `Searxes <https://searxes.danwin1210.me/>`__ @Danwin
     - onion v3 `hidden service
       <http://searxes.nmqnkngye4ct7bgss4bmv5ca3wpa55yugvxen5kz2bbq67lwy6ps54yd.onion/>`__
     - Let's Encrypt (`Verification
       <https://www.ssllabs.com/ssltest/analyze.html?d=searxes.danwin1210.me>`__)
     - sources data from a randomly selected running server that satisfies
       admin's quality standards which is used for post-processing
     - filters out privacy-hostile websites (like CloudFlare) and either marks
       them as such or folds them below the high ranking results.


Alive and running
=================

**BEFORE EDITING**: Please add your Searx instance by respecting the alphabetic order.

.. note::

   Public instances listed here may yield less accurate results as they have
   much higher traffic and consequently have a higher chance of being blocked by
   search providers such as Google, Qwant, Bing, Startpage, etc.  Hosting your
   own instance or using an instance that isn't listed here may give you a more
   consistent search experience.

* `ai.deafpray.wtf/searx <https://ai.deafpray.wtf/searx>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=ai.deafpray.wtf/searx>`__
* `bamboozle.it <https://bamboozle.it/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=bamboozle.it>`__
* `bee.jaekr.dev <https://bee.jaekr.dev>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=bee.jaekr.dev>`__
* `beezboo.com <https://beezboo.com/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=beezboo.com>`__
* `burtrum.org/searx <https://burtrum.org/searx>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=burtrum.org/searx>`__
* `darmarit.cloud/searx <https://darmarit.cloud/searx>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=darmarit.cloud/searx>`__
* `dc.ax <https://dc.ax>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=dc.ax>`__
* `dynabyte.ca <https://dynabyte.ca>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=dynabyte.ca>`__
* `goso.ga <https://goso.ga/search>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=goso.ga>`__
* `gruble.de <https://www.gruble.de/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=www.gruble.de>`__
* `haku.ahmia.fi <https://haku.ahmia.fi/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=haku.ahmia.fi&latest>`__
* `haku.lelux.fi <https://haku.lelux.fi/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=haku.lelux.fi>`__
* `huyo.me <https://huyo.me/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=huyo.me>`__
* `jsearch.pw <https://jsearch.pw>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=jsearch.pw>`__
* `le-dahut.com/searx <https://le-dahut.com/searx>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=le-dahut.com/searx>`__
* `mijisou.com <https://mijisou.com/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=mijisou.com>`__
* `null.media <https://null.media>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=null.media>`__
* `openworlds.info <https://openworlds.info/>`__ - Issuer: Let's Encrypt
* `perfectpixel.de/searx/ <https://www.perfectpixel.de/searx/>`__ - Issuer: LetsEncrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=www.perfectpixel.de>`__
* `ransack.i2p <http://ransack.i2p/>`__ - I2P eepsite, only accessible with `I2P <https://geti2p.net/>`__ (`base32 address <http://mqamk4cfykdvhw5kjez2gnvse56gmnqxn7vkvvbuor4k4j2lbbnq.b32.i2p>`__)
* `rapu.nz <https://rapu.nz/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=rapu.nz>`__
* `roflcopter.fr <https://wtf.roflcopter.fr/searx>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=wtf.roflcopter.fr>`__
* `roteserver.de/searx <https://roteserver.de/searx>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=roteserver.de>`__
* `s.cmd.gg <https://s.cmd.gg>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=s.cmd.gg>`__
* `search.activemail.de <https://search.activemail.de/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=search.activemail.de&latest>`__
* `search.anonymize.com <https://search.anonymize.com/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=search.anonymize.com>`__
* `search.azkware.net <https://search.azkware.net/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=search.azkware.net>`__
* `search.biboumail.fr <https://search.biboumail.fr/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=search.biboumail.fr>`__
* `search.blankenberg.eu <https://search.blankenberg.eu>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=search.blankenberg.eu>`__
* `search.d4networks.com <https://search.d4networks.com/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=search.d4networks.com>`__
* `search.datensturm.net <https://search.datensturm.net>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=search.datensturm.net>`__
* `search.disroot.org <https://search.disroot.org/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=search.disroot.org>`__
* `search.ethibox.fr <https://search.ethibox.fr>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=search.ethibox.fr>`__
* `search.fossdaily.xyz <https://search.fossdaily.xyz>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=search.fossdaily.xyz>`__
* `search.galaxy.cat <https://search.galaxy.cat>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=search.galaxy.cat>`__
* `search.gibberfish.org <https://search.gibberfish.org/>`__ (as `Hidden Service <http://o2jdk5mdsijm2b7l.onion/>`__ or `Proxied through Tor <https://search.gibberfish.org/tor/>`__) - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=search.gibberfish.org>`__
* `search.koehn.com <https://search.koehn.com>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=search.koehn.com>`__
* `search.lgbtq.cool <https://search.lgbtq.cool/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=search.lgbtq.cool>`__
* `search.mdosch.de <https://search.mdosch.de/>`__ (as `Hidden Service <http://search.4bkxscubgtxwvhpe.onion/>`__) - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=search.mdosch.de>`__
* `search.modalogi.com <https://search.modalogi.com/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=search.modalogi.com&latest>`__
* `search.moravit.com <https://search.moravit.com>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=search.moravit.com>`__
* `search.nebulacentre.net <https://search.nebulacentre.net>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=search.nebulacentre.net>`__
* `search.paulla.asso.fr <https://search.paulla.asso.fr/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=search.paulla.asso.fr>`__
* `search.pifferi.info <https://search.pifferi.info/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=search.pifferi.info&latest>`__
* `search.poal.co <https://search.poal.co/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=search.poal.co>`__
* `search.privacytools.io <https://search.privacytools.io/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=search.privacytools.io>`__ - Uses Matomo for user tracking and analytics
* `search.seds.nl <https://search.seds.nl/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=search.seds.nl&latest>`__
* `search.snopyta.org <https://search.snopyta.org/>`__ (as `Hidden Service <http://juy4e6eicawzdrz7.onion/>`__) - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=search.snopyta.org>`__
* `search.spaeth.me <https://search.spaeth.me/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=search.spaeth.me&latest>`__
* `search.st8.at <https://search.st8.at/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=search.st8.at>`__
* `search.stinpriza.org <https://search.stinpriza.org>`__ (as `Hidden Service <http://z5vawdol25vrmorm4yydmohsd4u6rdoj2sylvoi3e3nqvxkvpqul7bqd.onion/>`__) - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=search.stinpriza.org&hideResults=on>`__
* `search.sudo-i.net <https://search.sudo-i.net/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=search.sudo-i.net>`__
* `search.tolstoevsky.ml <https://search.tolstoevsky.ml>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=search.tolstoevsky.ml>`__
* `searchsin.com/searx <https://searchsin.com/searx>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searchsin.com/searx>`__
* `searx.anongoth.pl <https://searx.anongoth.pl>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.anongoth.pl&latest>`__
* `searx.be <https://searx.be>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.be>`__ - Uses Fathom Analytics for user tracking and analytics
* `searx.ca <https://searx.ca/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.ca>`__
* `searx.canox.net <https://searx.canox.net/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.canox.net>`__
* `searx.cybt.de <https://searx.cybt.de/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.cybt.de>`__
* `searx.de <https://www.searx.de/>`__ - Issuer: COMODO `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.de>`__
* `searx.decatec.de <https://searx.decatec.de>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.decatec.de>`__
* `searx.devol.it <https://searx.devol.it/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=sears.devol.it>`__
* `searx.dnswarden.com <https://searx.dnswarden.com>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.dnswarden.com>`__
* `searx.drakonix.net <https://searx.drakonix.net/>`__ - (down) Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.drakonix.net>`__
* `searx.dresden.network <https://searx.dresden.network/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.dresden.network>`__
* `searx.elukerio.org <https://searx.elukerio.org/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.elukerio.org/>`__
* `searx.everdot.org <https://searx.everdot.org/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.everdot.org/>`__ - Crawls using YaCy
* `searx.foo.li <https://searx.foo.li>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.foo.li&hideResults=on>`__
* `searx.fossencdi.org <https://searx.fossencdi.org>`__ (as `Hidden Service <http://searx.cwuzdtzlubq5uual.onion/>`__) - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.fossencdi.org>`__
* `searx.fr32k.de <https://searx.fr32k.de/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.fr32k.de>`__
* `searx.good.one.pl <https://searx.good.one.pl>`__ (as `Hidden Service <http://searxl7u2y6gvonm.onion/>`__) - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.good.one.pl>`__
* `searx.gotrust.de <https://searx.gotrust.de/>`__ (as `Hidden Service <http://nxhhwbbxc4khvvlw.onion/>`__)  - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.gotrust.de>`__
* `searx.hardwired.link <https://searx.hardwired.link/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.hardwired.link>`__
* `searx.hlfh.space <https://searx.hlfh.space>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.hlfh.space>`__
* `searx.info <https://searx.info>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.info>`__
* `searx.itunix.eu <https://searx.itunix.eu/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.itunix.eu>`__
* `searx.john-at-me.net <https://searx.john-at-me.net/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.john-at-me.net>`__
* `searx.kvch.me <https://searx.kvch.me>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.kvch.me>`__
* `searx.laquadrature.net <https://searx.laquadrature.net>`__ (as `Hidden Service <http://searchb5a7tmimez.onion/>`__) - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.laquadrature.net>`__
* `searx.lelux.fi <https://searx.lelux.fi/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=haku.lelux.fi>`__
* `searx.lhorn.de <https://searx.lhorn.de/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.lhorn.de&latest>`__
* `searx.li <https://searx.li/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.li>`__
* `searx.libmail.eu <https://searx.libmail.eu/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.libmail.eu/>`__
* `searx.linux.pizza <https://searx.linux.pizza>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.linux.pizza>`__
* `searx.lynnesbian.space <https://searx.lynnesbian.space/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.lynnesbian.space>`__
* `searx.mastodontech.de <https://searx.mastodontech.de/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.mastodontech.de>`__
* `searx.me <https://searx.me>`__ (as `Hidden Service <http://ulrn6sryqaifefld.onion/>`__) - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.me>`__
* `searx.mxchange.org <https://searx.mxchange.org/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.mxchange.org>`__
* `searx.nakhan.net <https://searx.nakhan.net>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.nakhan.net>`__
* `searx.nixnet.xyz <https://searx.nixnet.xyz>`__ (as `Hidden Service <http://searx.l4qlywnpwqsluw65ts7md3khrivpirse744un3x7mlskqauz5pyuzgqd.onion/>`__) - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.nixnet.xyz>`__
* `searx.nnto.net <https://searx.nnto.net/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.nnto.net>`__
* `searx.openhoofd.nl <https://searx.openhoofd.nl/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=openhoofd.nl>`__
* `searx.openpandora.org <https://searx.openpandora.org/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.openpandora.org&latest>`__
* `searx.operationtulip.com <https://searx.operationtulip.com/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.operationtulip.com>`__
* `searx.orcadian.net <https://searx.orcadian.net/>`__ - Issuer: Comodo CA Limited `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.orcadian.net>`__
* `searx.ouahpit.info <https://searx.ouahpiti.info/>`__ - Issuer: Let's Encrypt
* `searx.pofilo.fr <https://searx.pofilo.fr/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.pofilo.fr>`__
* `searx.prvcy.eu <https://searx.prvcy.eu/>`__ (as `Hidden Service <http://hmfztxt3pfhevucl.onion/>`__) - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.prvcy.eu>`__
* `searx.pwoss.org <https://searx.pwoss.org>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.pwoss.org>`__
* `searx.ro <https://searx.ro/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.ro>`__
* `searx.ru <https://searx.ru/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.ru>`__
* `searx.solusar.de <https://searx.solusar.de/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.solusar.de>`__
* `searx.targaryen.house <https://searx.targaryen.house/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.targaryen.house>`__
* `searx.tuxcloud.net <https://searx.tuxcloud.net>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.tuxcloud.net>`__
* `searx.tyil.nl <https://searx.tyil.nl>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.tyil.nl>`__
* `searx.wegeeks.win <https://searx.wegeeks.win>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.wegeeks.win>`__
* `searx.win <https://searx.win/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.win&latest>`__
* `searx.xyz <https://searx.xyz/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.xyz&latest>`__
* `searx.zareldyn.net <https://searx.zareldyn.net/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.zareldyn.net>`__
* `searx.zdechov.net <https://searx.zdechov.net>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.zdechov.net>`__
* `searxs.eu <https://www.searxs.eu>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=www.searxs.eu&hideResults=on>`__
* `seeks.hsbp.org <https://seeks.hsbp.org/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=seeks.hsbp.org>`__ - `PGP signed fingerprints of cert <https://seeks.hsbp.org/cert>`__
* `skyn3t.in/srx <https://skyn3t.in/srx/>`__ - Issuer: Let's Encrypt | onion `hidden service <http://skyn3tb3bas655mw.onion/srx/>`__
* `spot.ecloud.global <https://spot.ecloud.global/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=spot.ecloud.global>`__
* `srx.sx <https://srx.sx>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=srx.sx>`__
* `stemy.me/searx <https://stemy.me/searx>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=stemy.me>`__
* `suche.dasnetzundich.de <https://suche.dasnetzundich.de>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=suche.dasnetzundich.de>`__
* `suche.elaon.de <https://suche.elaon.de>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=suche.elaon.de>`__
* `suche.xyzco456vwisukfg.onion <http://suche.xyzco456vwisukfg.onion/>`__
* `suche.uferwerk.org <https://suche.uferwerk.org>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=suche.uferwerk.org>`__
* `timdor.noip.me/searx <https://timdor.noip.me/searx>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=timdor.noip.me/searx>`__
* `trovu.komun.org <https://trovu.komun.org>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=trovu.komun.org>`__
* `unmonito.red <https://unmonito.red/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=unmonito.red>`__
* `www.finden.tk <https://www.finden.tk/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=www.finden.tk>`__
* `zoek.anchel.nl <https://zoek.anchel.nl/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=zoek.anchel.nl>`__



Running in exclusive private walled-gardens
===========================================

These instances run in walled-gardens that exclude some segment of the general
public (e.g. Tor users and users sharing IPs with many other users).  Caution:
privacy is also compromised on these sites due to exposure of cleartext traffic
to a third party other than the website operator.

* `intelme.com <https://intelme.com>`__ - Issuer: Cloudflare `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=intelme.com>`__
* `search404.io <https://www.search404.io/>`__ - Issuer: Cloudflare `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=search404.io>`__ 
* `searx.com.au <https://searx.com.au/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.com.au>`__
* `searx.lavatech.top <https://searx.lavatech.top/>`__ - Issuer: Cloudflare `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.lavatech.top>`__
* `searchx.mobi <https://searchx.mobi/>`__ - Issuer: Cloudflare `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searchx.mobi>`__
* `searx.org <https://searx.org/>`__ - Issuer: Cloudflare `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.org>`__ 
* `searx.run <https://searx.run/>`__ - Issuer: Cloudflare `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.run>`__
* `searx.world <https://searx.world>`__ - Issuer: Cloudflare `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.world>`__ - Adds Amazon affiliate links


Running with an incorrect SSL certificate
=========================================

* `listi.me <https://listi.me/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=listi.me&latest>`__
* `s.matejc.com <https://s.matejc.com/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=s.matejc.com>`__
* `search.jollausers.de <https://search.jollausers.de>`__ - Incorrectly configured `SSL certificate <https://www.ssllabs.com/ssltest/analyze.html?d=search.jollausers.de>`__
* `search.paviro.de <https://search.paviro.de>`__ - Issuer: LetsEncrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=search.paviro.de>`__
* `searx.abenthung.it <https://searx.abenthung.it/>`__ - Issuer: Comodo CA Limited `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.abenthung.it>`__
* `searx.coding4schoki.org <https://searx.coding4schoki.org/>`__ - Incorrectly configured `SSL Certificate <https://www.ssllabs.com/ssltest/analyze.html?d=searx.coding4schoki.org>`__
* `searx.haxors.club <https://searx.haxors.club/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.haxors.club>`__
* `searx.nulltime.net <https://searx.nulltime.net/>`__ (as `Hidden Service <http://searx7gwtu5rh6wr.onion>`__) - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.nulltime.net>`__
* `searx.ch <https://searx.ch/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.ch>`__ (cert clock problems)


Offline
=======

* `a.searx.space <https://a.searx.space>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=a.searx.space>`__ (unstable, under construction).
* `anyonething.de <https://anyonething.de>`__ - (was found to have become a pastebin on or before 2019-03-01) Issuer: Comodo CA Limited (Warning: uses Cloudflare) `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=anyonething.de>`__
* `h7jwxg5rakyfvikpi.onion <http://7jwxg5rakyfvikpi.onion/>`__ - available only as Tor Hidden Service (down on 2019-06-26)
* `hacktivis.me/searx <https://hacktivis.me/searx>`__ - (down) - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=hacktivis.me/searx>`__
* `icebal.com <https://icebal.com>`__ - (down) Issuer: Let's Encrypt
* `netrangler.host <https://netrangler.host>`__ - (down) - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=netrangler.host>`__
* `opengo.nl <https://www.opengo.nl>`__ - (down) Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=www.opengo.nl>`__
* `p9e.de <https://p9e.de/>`__ - (down - timeout) Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=p9e.de>`__
* `rubri.co <https://rubri.co>`__ - (down) Issuer: Let's Encrypt
* `s.bacafe.xyz <https://s.bacafe.xyz/>`__ - (down) Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=s.bacafe.xyz&latest>`__
* `search.alecpap.com <https://search.alecpap.com/>`__ - (down) Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=search.alecpap.com>`__
* `search.blackit.de <https://search.blackit.de/>`__ - (down) Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=search.blackit.de>`__
* `search.deblan.org <https://search.deblan.org/>`__ (down) - Issuer: COMODO via GANDI `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=search.deblan.org>`__
* `search.homecomputing.fr <https://search.homecomputing.fr/>`__ - (down) Issuer: CAcert `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=search.homecomputing.fr>`__
* `search.jpope.org <https://search.jpope.org>`__ - (down - timeout) Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=search.jpope.org>`__
* `search.kakise.xyz <https://search.kakise.xyz/>`__ - down
* `search.kosebamse.com <https://search.kosebamse.com>`__ - Issuer: LetsEncrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=search.kosebamse.com>`__
* `search.kujiu.org <https://search.kujiu.org>`__ - (down) Issuer: Let's Encrypt
* `search.mailaender.coffee <https://search.mailaender.coffee/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=search.mailaender.coffee>`__
* `search.matrix.ac <https://search.matrix.ac>`__ - (down) Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=matrix.ac>`__
* `search.mypsc.ca <https://search.mypsc.ca/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=search.mypsc.ca>`__
* `search.namedkitten.pw <https://search.namedkitten.pw>`__ - (SSL error) - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=search.namedkitten.pw>`__
* `search.opentunisia.org <https://search.opentunisia.org>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=search.opentunisia.org>`__
* `search.r3d007.com <https://search.r3d007.com/>`__ - (down) Issuer: Let's Encrypt
* `search.static.lu <https://search.static.lu/>`__ - (down) Issuer: StartCom `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=search.static.lu>`__
* `search.teej.xyz <https://search.teej.xyz>`__ - (down) Issuer: LetsEncrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=search.teej.xyz>`__
* `search.wxzm.sx <https://search.wxzm.sx>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=search.wxzm.sx>`__
* `searx.4ray.co <https://searx.4ray.co/>`__ - (no longer an instance, redirects to main page) Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.4ray.co>`__
* `searx.32bitflo.at <https://searx.32bitflo.at/>`__ - (down) Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.32bitflo.at>`__
* `searx.ahh.si <https://searx.ahh.si/>`__ - (down) - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.ahh.si>`__ 
* `searx.angristan.xyz <https://searx.angristan.xyz/>`__ - (down) Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.angristan.xyz>`__
* `searx.antirep.net <https://searx.antirep.net/>`__ - (return a 502 HTTP error) Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.antirep.net>`__
* `searx.aquilenet.fr <https://searx.aquilenet.fr/>`__ - (down - 429 HTTP error) Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.aquilenet.fr>`__
* `searx.at <https://searx.at/>`__ - (return "request exception" at every search) Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.at>`__
* `searx.cc <https://searx.cc/>`__ - (down on 2019-06-26) Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.cc>`__ 
* `searx.dk <https://searx.dk/>`__ - (down - 429 HTTP error) Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.dk>`__
* `searx.ehrmanns.ch <https://searx.ehrmanns.ch>`__ - (down) Issuer: Let's Encrypt 
* `searx.glibre.net <https://searx.glibre.net>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.glibre.net>`__
* `searx.infini.fr <https://searx.infini.fr>`__ - (return a page stating that the website is not installed) Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.infini.fr>`__
* `searx.jeanphilippemorvan.info <https://searx.jeanphilippemorvan.info/>`__ - (down) Issuer: StartCom `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.jeanphilippemorvan.info>`__
* `searx.lhorn.de <https://searx.lhorn.de/>`__ - (redirect the Searx's github repository page) Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.lhorn.de&latest>`__ (only reachable from european countries)
* `searx.lvweb.host <https://searx.lvweb.host>`__ - (down) Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.lvweb.host>`__
* `searx.mrtino.eu <https://searx.mrtino.eu>`__ - (down) Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.mrtino.eu>`__
* `searx.netzspielplatz.de <https://searx.netzspielplatz.de/>`__ - (error page about GDPR even when browsing it from USA and Asia) - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.netzspielplatz.de>`__
* `searx.new-admin.net <https://searx.new-admin.net>`__ - (down) Issuer: Let's Encrypt
* `searx.nogafa.org <https://searx.nogafa.org/>`__ - (broken CSS) Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.nogafa.org>`__
* `searx.potato.hu <https://searx.potato.hu>`__ - (not a searx instance) - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.potato.hu>`__
* `searx.rubbeldiekatz.info <https://searx.rubbeldiekatz.info/>`__ - (down) Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.rubbeldiekatz.info/>`__
* `searx.s42.space <https://searx.s42.space>`__ - (down) Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.s42.space>`__
* `searx.salcay.hu <https://searx.salcay.hu/>`__ - (down - blank page) Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.salcay.hu>`__
* `searx.selea.se <https://searx.selea.se>`__ - (Leads to default Apache page) Issuer: RapidSSL (HSTS preloaded, DNSSEC) `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.selea.se>`__ | `HSTS Preload <https://hstspreload.org/?domain=searx.selea.se>`__
* `searx.steinscraft.net <https://searx.steinscraft.net/>`__ - (down) Issuer: Cloudflare
* `searx.techregion.de <https://searx.techregion.de/>`__ - (domain expired) - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.techregion.de>`__
* `searx.tognella.com <https://searx.tognella.com/>`__ - (down) Issuer: Cloudflare
* `searx.xi.ht <https://searx.xi.ht/>`__ - (return a 502 HTTP error) Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searx.xi.ht>`__
* `searxist.com <https://searxist.com/>`__ - (down) - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=searxist.com>`__
* `so.sb <https://so.sb/>`__ - (down) - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=so.sb>`__
* `srx.stdout.net <https://srx.stdout.net/>`__ - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=srx.stdout.net>`__
* `w6f7cgdm54cyvohcuhraaafhajctyj3ihenrovuxogoagrr5g43qmoid.onion <http://w6f7cgdm54cyvohcuhraaafhajctyj3ihenrovuxogoagrr5g43qmoid.onion/>`__ - Hidden Service
* `win8linux.nohost.me <https://win8linux.nohost.me/searx/>`__ - (down) Issuer: Let's Encrypt
* `wiznet.tech <https://wiznet.tech>`__ - (down) - Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=wiznet.tech>`__
* `www.mercurius.space <https://www.mercurius.space/>`__ - (down) Issuer: Let's Encrypt
* `www.ready.pm <https://www.ready.pm>`__ - Issuer: WoSign `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=www.ready.pm>`__
* `z.awsmppl.com <https://z.awsmppl.com>`__ - (down) Issuer: Let's Encrypt `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=z.awsmppl.com>`__
* `zlsdzh.tk <https://zlsdzh.tk>`__ - (down - 404 HTTP error) Issuer: TrustAsia Technologies, Inc. `Verification <https://www.ssllabs.com/ssltest/analyze.html?d=zlsdzh.tk>`__ *

