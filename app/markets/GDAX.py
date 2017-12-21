import requests

import json, hmac, hashlib, time, requests, base64
from requests.auth import AuthBase

# sandbox api base
#api_base = 'https://api-public.sandbox.gdax.com'

# api base
api_base = 'https://api.gdax.com'

# Create custom authentication for Exchange
class gdaxAuth(AuthBase):
    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase

    def __call__(self, request):
        timestamp = str(time.time())
        message = timestamp + request.method + request.path_url + (request.body or '')
        hmac_key = base64.b64decode(self.secret_key)
        signature = hmac.new(hmac_key, message, hashlib.sha256)
        signature_b64 = signature.digest().encode('base64').rstrip('\n')

        request.headers.update({
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        })
        return request

class gdax:
    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase

    def get_ticker(self, pair):
        response = requests.get(api_base + '/products/' + pair + '/ticker')
        # check for invalid api response
        if response.status_code is not 200:
            raise Exception('Invalid GDAX Status Code: %d' % response.status_code)
        return response.json()

    def get_balances(self):

        auth = gdaxAuth(self.api_key, self.secret_key, self.passphrase)
        res = requests.get(api_base + '/accounts', auth=auth)

        if res.status_code is not 200:
            raise Exception('Invalid GDAX Status Code: %d' % res.status_code)
        return res.json()

    def place_order(self, market, side, product_id, size ):
        auth = gdaxAuth(self.api_key, self.secret_key, self.passphrase)
        order_url = api_base + '/orders'
        order_data = {
            'type': market,
            'side': side,
            'product_id': product_id,
            'size': size
        }
        response = requests.post(order_url, data=json.dumps(order_data), auth=auth)
        print(response.json())

    def place_limit_order(self, side, product_id, price, size):
        auth = gdaxAuth(self.api_key, self.secret_key, self.passphrase)
        order_url = api_base + '/orders'
        order_data = {
            'price': price,
            'side': side,
            'product_id': product_id,
            'size': size
        }
        response = requests.post(order_url, data=json.dumps(order_data), auth=auth)
        print(response.json())

    def cancel_order(self, order_id):
        auth = gdaxAuth(self.api_key, self.secret_key, self.passphrase)
        res = requests.delete(api_base + '/orders/' + order_id, auth=auth)

        if res.status_code is not 200:
            raise Exception('Invalid GDAX Status Code: %d' % res.status_code)
        return res.json()

    def cancel_order_all(self):
        auth = gdaxAuth(self.api_key, self.secret_key, self.passphrase)
        res = requests.delete(api_base + '/orders/', auth=auth)

        if res.status_code is not 200:
            raise Exception('Invalid GDAX Status Code: %d' % res.status_code)
        return res.json()
    def _post(self, command, payload):
        pass
    