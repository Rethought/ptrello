"""
Basic Trello API wrapper. Unlike others on the web this tries to be
clever and very light and not require updating if the API is extended.
On the other hand it has some obvious issues that a code review will
pick up quite quickly :D

The idea is that the calling mechanism maps clearly to the URLs. So if the
documentation says you can call:

  GET /1/boards/[board_id]/lists/[filter]

You will be able to do:

   trello.boards[BOARD_ID].lists[FILTER]()

All names and arguments get mapped into a URL path. So the above becomes:
 
   /boards/BOARD_ID/lists/FILTER

Keyword arguments sent as parameters when making the call get sent as URL
arguments.

POST not yet supported but will be done at some point.
"""
import requests
import json


class Trello(object):
    """
    Wrap up calls to the Trello API. Only GET requests for now.
    """
    def __init__(self,
                 api_key,
                 api_token,
                 root_url="https://trello.com/1/",
                 ):
        self.api_key = api_key
        self.api_token = api_token
        self.default_params = {'key': self.api_key,
                               'token': self.api_token}
        self.root_url = root_url
        self._conn = None

    def request(self, path, **params):
        """
        Make a call to the Trello API.
        """
        url = self.root_url + path
        params.update(self.default_params)
        rv = requests.get(url, params=params)
        return json.loads(rv.content)

    def __getattr__(self, key):
        """
        Return a TrelloCall wrapper to build the request
        """
        return TrelloCall(self, key)

    def __getitem__(self, key):
        """
        Return a TrelloCall wrapper to biuld the request
        """
        return TrelloCall(self, key)


class TrelloCall(object):
    """
    We want to provide an idiom that maps to the API transparently so that
    you can call:

      $ trello.boards[board_id].cards()

    and do this in a form that is thread safe. As each term in the
    dotted sequence becomes part of the URL we need to convert that
    into a list. This class makes that happen and then the final
    call is done using the Trello instance with which it was initialised.

    The final `request` is, of course, a real method call that makes
    the Trello request.

    The Trello class will transparently return this from it's __getattr__
    or __getitem__ so from a user perspective it's all quite transparent.

    You should not store a TrelloCall instance and use multiple times because
    of the simple way it builds arguments. For example, this is an obvious
    failure mode:

      > r = trello.boards["asjflkdsjflkdsajflksaj"]
      > lists = r.lists() # OK
      > cards = r.cards() # UH OH - FAIL

    The last call fails because the call made is to the non-sensical
    path `/boards/asjflkdsjflkdsajflksaj/lists/cards/`.

    Also if thousands of calls are being made, lots of TrelloCall instances
    will be made for the GC to deal with. It's all a bit ungainly really.
    """
    def __init__(self, trello, first_arg):
        """
        Initialise the wrapper with a Trello instance, passing in
        the key that caused Trello to instantiate this object.
        """
        self.args = [first_arg]
        self.trello = trello

    def __getattr__(self, key):
        self.args.append(key)
        return self


    def __getitem__(self, key):
        self.args.append(key)
        return self

    def __call__(self, **kwargs):
        """
        Make the request to Trello and return the response. **kwargs
        are sent as get args.
        """
        return self.trello.request("/".join(self.args), **kwargs)
