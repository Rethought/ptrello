Trello board printer
====================

Quick 'n' dirty utility to render out board tickets from Trello, getting data
via their API.

This is published in the interests of sharing but without any implication that
this constitutes a polished product for general use. If you find it useful,
we're happy! You'll need to edit and play to  make it suit your needs I am
sure.

Implementation
--------------
You will need to install the requirements from `requirements.txt` - the only
dependencies are:

  * Jinja2
  * requests

Then copy `example_settings.py` to `settings.py` and set values to the
API keys and tokens you can create  at
https://trello.com/docs/gettingstarted/index.html#getting-an-application-key

Find other information at https://trello.com/b/cI66RoQS/trello-public-api

Use
---

Run::

  > ptrello.py -h

to see the options available to you.

Example usage::

  > ptrello.py --prune --title="My Lovely Board" > stories.html

The ReThought team
http://www.rethought-solutions.com

Tests
-----
To run tests you will need to install the requirements from
`test_requirements.txt` and run:

  > nosetests -v

And a handful of tests will be executed.
