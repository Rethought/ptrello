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

Use
---

Run::

  > ptrello.py -h

to see the options available to you.

The ReThought team
http://www.rethought-solutions.com
