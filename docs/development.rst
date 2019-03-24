Development
###########

This is a small guide on setting up a development environment for ``unchaind``.
``unchaind`` requires Python 3.6 or higher which is included by default in
Ubuntu 18.04 or other distributions around this time.

git checkout
------------
Start by creating a fork on github_. Then clone the repository into a local
checkout with ``git clone https://github.com/username/unchaind``. This will
allow you to create pull requests later on.

Virtual Environment
-------------------
Now enter your checkout with ``cd unchaind/`` and create a virtual environment.
This will allow you to keep all your dependencies local to your environment
instead of clobbering the system. You can do this by doing a quick
``python3.6 -m venv .venv`` and then a ``source .venv/bin/activate`` to put the
environments environment variables to use.

After this you can install all required dependencies for ``unchaind`` with
the following two commands: ``python setup.py develop`` and 
``pip install -e .[dev]`` to install everything necessary into your local
environment.

Running tests
-------------
``unchaind`` ships with the ``pre-commit`` package which you installed
previously. You can set these up to automatically run some sanity checks
before you commit any code. Do so by running ``pre-commit install`` in the
checkout directory.

Doing work
----------
Any pull requests are welcome but especially those involving our current
issues_. There's some marked as a `good first issue` but you can try
your hand at any. Just let us know in the issues_ that you are working on a
pull request for them!

.. _github: https://github.com/supakeen/unchaind
.. _issues: https://github.com/supakeen/unchaind/issues
