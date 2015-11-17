How to contribute
-----------------

Prime directives: Privacy, Hackability
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Searx has 2 prime directives, privacy-by-design and hackability. The
hackability comes in at least 3 levels:

-  support for search engines
-  plugins for altering search behaviour
-  hacking searx itself.

Happy hacking. Observe the lack of "world domination" among the
directives, searx has no intentions for wide mass-adoption, rounded
corners, etc. The prime directive: "privacy" - deserves a seperate
chapter, as it's quite uncommon unfortunately, here it goes:

Privacy-by-design
^^^^^^^^^^^^^^^^^

Searx is a privacy-respecting, hackable meta-search engine. It was born
out of the need for a privacy-respecing search facility that can be
expanded easily to maximise both its search and it's privacy protecting
capabilities.

Consequences of Privacy-by-design are that some widely used features
work differently or not by default or at all. If some feature reduces
the privacy perserving aspects of searx, it should by default be
switched of, if implemented at all. There is enough search engines
already out there providing such features. = Since privacy-preservation
is a prime goal, if some feature does reduce the protection of searx and
is implemented, care should be taken to educate the user about the
consequences of choosing to enable this. Further features which
implement widely known features in a manner that protects privacy but
thus deviate from the users expectations should also be explained to the
user. Also if you think that something works weird with searx, maybe
it's because of the tool you use is designed in a way to interfere with
privacy respect, submiting a bugreport to the vendor of the tool that
misbehaves might be a good feedback for the vendor to reconsider his
disrespect towards his customers (e.g. GET vs POST requests in various
browsers).

Remember the other prime directive of searx is to be hackable, so if the
above privacy concerns do not fancy you, simply fork it.

Code
~~~~

Code modifications are accepted in pull requests, don't forget to add
yourself to the AUTHORS file.

Python code follows all the pep8 standards except maximum line width
which is 120 char.

Please be sure that the submitted code doesn't break existing tests and
follows coding conventions.

If new functionality implemented, tests are highly appreciated.

Translation
~~~~~~~~~~~

Translation currently happens on
`transifex <https://transifex.com/projects/p/searx>`__. Please do not
update translation files in the repo.

Documentation
~~~~~~~~~~~~~

The main place of the documentation is this wiki, updates are welcome.
