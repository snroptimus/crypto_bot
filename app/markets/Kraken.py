import requests

# private query nonce
import time

# private query signing
try:
    from urllib import urlencode
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urlencode
    from urllib.parse import urljoin
import hashlib
import hmac
import base64

__version__ = '2.0.0'
__url__ = 'https://github.com/veox/python3-krakenex'

class Kraken(object):
    """ Maintains a single session between this machine and Kraken.
    Specifying a key/secret pair is optional. If not specified, private
    queries will not be possible.
    The :py:attr:`session` attribute is a :py:class:`requests.Session`
    object. Customise networking options by manipulating it.
    Query responses, as received by :py:mod:`requests`, are retained
    as attribute :py:attr:`response` of this object. It is overwritten
    on each query.
    .. note::
       No query rate limiting is performed.
    """
    def __init__(self, key='', secret=''):
        """ Create an object with authentication information.
        :param key: (optional) key identifier for queries to the API
        :type key: str
        :param secret: (optional) actual private key used to sign messages
        :type secret: str
        :returns: None
        """
        self.key = key
        self.secret = secret
        self.uri = 'https://api.kraken.com'
        self.apiversion = '0'
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'krakenex/' + __version__ + ' (+' + __url__ + ')'
        })
        self.response = None
        return

    def close(self):
        """ Close this session.
        :returns: None
        """
        self.session.close()
        return

    def load_key(self, path):
        """ Load key and secret from file.
        Expected file format is key and secret on separate lines.
        :param path: path to keyfile
        :type path: str
        :returns: None
        """
        with open(path, 'r') as f:
            self.key = f.readline().strip()
            self.secret = f.readline().strip()
        return

    def _query(self, urlpath, data, headers=None):
        """ Low-level query handling.
        .. note::
           Use :py:meth:`query_private` or :py:meth:`query_public`
           unless you have a good reason not to.
        :param urlpath: API URL path sans host
        :type urlpath: str
        :param data: API request parameters
        :type data: dict
        :param headers: (optional) HTTPS headers
        :type headers: dict
        :returns: :py:meth:`requests.Response.json`-deserialised Python object
        :raises: :py:exc:`requests.HTTPError`: if response status not successful
        """
        if data is None:
            data = {}
        if headers is None:
            headers = {}

        url = self.uri + urlpath

        print(url)
        self.response = self.session.post(url, data = data, headers = headers)

        if self.response.status_code not in (200, 201, 202):
            self.response.raise_for_status()

        return self.response.json()


    def query_public(self, method, data=None):
        """ Performs an API query that does not require a valid key/secret pair.
        :param method: API method name
        :type method: str
        :param data: (optional) API request parameters
        :type data: dict
        :returns: :py:meth:`requests.Response.json`-deserialised Python object
        """
        if data is None:
            data = {}

        urlpath = '/' + self.apiversion + '/public/' + method

        return self._query(urlpath, data)

    def get_ticker(self, pair):
        res = requests.get("https://api.kraken.com/0/public/Ticker?pair=" + pair)
        return res.json()["result"][pair]["c"]

    def query_private(self, method, data=None):
        """ Performs an API query that requires a valid key/secret pair.
        :param method: API method name
        :type method: str
        :param data: (optional) API request parameters
        :type data: dict
        :returns: :py:meth:`requests.Response.json`-deserialised Python object
        """
        if data is None:
            data = {}

        if not self.key or not self.secret:
            raise Exception('Either key or secret is not set! (Use `load_key()`.')

        data['nonce'] = self._nonce()

        urlpath = '/' + self.apiversion + '/private/' + method

        headers = {
            'API-Key': self.key,
            'API-Sign': self._sign(data, urlpath)
        }

        return self._query(urlpath, data, headers)

    def _nonce(self):
        """ Nonce counter.
        :returns: an always-increasing unsigned integer (up to 64 bits wide)
        """
        return int(1000*time.time())

    def _sign(self, data, urlpath):
        """ Sign request data according to Kraken's scheme.
        :param data: API request parameters
        :type data: dict
        :param urlpath: API URL path sans host
        :type urlpath: str
        :returns: signature digest
        """
        postdata = urlencode(data)

        # Unicode-objects must be encoded before hashing
        encoded = (str(data['nonce']) + postdata).encode()
        message = urlpath.encode() + hashlib.sha256(encoded).digest()

        signature = hmac.new(base64.b64decode(self.secret),
                             message, hashlib.sha512)
        sigdigest = base64.b64encode(signature.digest())

        return sigdigest.decode()
    
    def create_order(self, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        order = {
            'pair': market['id'],
            'type': side,
            'ordertype': type,
            'volume': self.amount_to_precision(symbol, amount),
        }
        if type == 'limit':
            order['price'] = self.price_to_precision(symbol, price)
        response = self.privatePostAddOrder(self.extend(order, params))
        length = len(response['result']['txid'])
        id = response['result']['txid'] if (length > 1) else response['result']['txid'][0]
        return {
            'info': response,
            'id': id,
        }