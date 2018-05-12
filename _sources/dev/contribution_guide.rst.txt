How to contribute
-----------------

Prime directives: Privacy, Hackability
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Searx has two prime directives, privacy-by-design and hackability. The
hackability comes in three levels:

-  support of search engines
-  plugins to alter search behaviour
-  hacking searx itself

Note the lack of "world domination" among the directives.
Searx has no intention of wide mass-adoption, rounded
corners, etc. The prime directive "privacy" deserves a separate
chapter, as it's quite uncommon unfortunately.

Privacy-by-design
^^^^^^^^^^^^^^^^^

Searx was born out of the need for a privacy-respecting search tool
which can be extended easily to maximize both its search and its
privacy protecting capabilities.

A few widely used features work differently or turned off by default or not implemented
at all as a consequence of privacy-by-design.

If a feature reduces the privacy preserving aspects of searx, it
should be switched off by default or should not implemented at all.
There are plenty of search engines already providing such features.
If a feature reduces the protection of searx, users must be
informed about the effect of choosing to enable it. Features
that protect privacy but differ from the expectations of the
user should also be explained.

Also, if you think that something works weird with searx,
it's might be because of the tool you use is designed in a way to interfere with
the privacy respect. Submitting a bugreport to the vendor of the tool that
misbehaves might be a good feedback to reconsider the disrespect to
its customers (e.g. GET vs POST requests in various browsers).

Remember the other prime directive of searx is to be hackable, so if the
above privacy concerns do not fancy you, simply fork it.

Happy hacking.

Code
~~~~

In order to submit a patch, please follow the steps below:

- Follow coding conventions.

  - PEP8 standards apply, except the convention of line length

  - Maximum line length is 120 characters

- Check if your code breaks existing tests. If so, update the tests or fix your code.

- If your code can be unit-tested, add unit tests.

- Add yourself to the AUTHORS file.

- Create a pull request.

For more help on getting started with searx development, see :ref:`devquickstart`.


Translation
~~~~~~~~~~~

Translation currently takes place on
`transifex <https://transifex.com/projects/p/searx>`__.

**Please, do not update translation files in the repo.**

Documentation
~~~~~~~~~~~~~

The documentation is built using Sphinx. So in order to be able to generate the required
files, you have to install it on your system. (It can be installed easily using pip.)

1. Checkout the gh-pages branch.

2. Edit the rst file you wish to update. Or create a new rst file and place it under the appropriate folder.

3. Build the documentation using Sphinx.

4. Add the updated and created files of these extension:

   - .rst

   - .html

   - .txt

6. Create a pull request.
