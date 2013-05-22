"""
Basic tests of the Trello API wrapper
"""
from trello import Trello
from trello import TrelloCall
from mock import patch


def fake_request(self, path, **params):
    """
    Used when mocking out Trello.request for testing
    """
    return (path, params)


class TestWrapper(object):
    def setup(self):
        self.trello = Trello("fakekey", "faketoken")

    def test_getattr_on_trello(self):
        """
        Ensure Trello getattr returns TrelloCall
        """
        v = self.trello.obj
        assert isinstance(v, TrelloCall)

    def test_getitem_on_trello(self):
        """
        Ensure Trello getitem returns TrelloCall
        """
        v = self.trello['obj']
        assert isinstance(v, TrelloCall)

    def test_url_with_attrs(self):
        """
        Test URL construction with attributes
        """
        v = self.trello.path.to.resource
        assert v.args == ['path', 'to', 'resource']

    def test_url_with_items(self):
        """
        Test URL construction with indexing
        """
        v = self.trello.resource['id001']
        assert v.args == ['resource', 'id001']

    def test_url_with_mixed_keys(self):
        """
        Test URL construction with attributes and items
        """
        v = self.trello.path.to.resource['id001']
        assert v.args == ['path', 'to', 'resource', 'id001']

    @patch("trello.Trello.request", fake_request)
    def test_call_to_request(self):
        """
        Test parameters sent to Trello.request
        """
        path, params = self.trello.path.to.resource['id001']()
        assert path == "path/to/resource/id001"

    @patch("trello.Trello.request", fake_request)
    def test_call_to_request_with_params(self):
        """
        Test parameters sent to Trello.request with getargs
        """
        path, params = self.trello.path.to.resource['id001'](a=10, b=20)
        assert path == "path/to/resource/id001"
        assert params == dict(a=10, b=20)
