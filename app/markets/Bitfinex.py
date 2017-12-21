# coding=utf-8
import hashlib
import hmac
import base64
import json
import requests
import time

class ApiError(Exception):
    pass


class Bitfinex():
    def __init__(self, cfg, log, apikey, secret):
        self.cfg = cfg
        self.log = log
        self.url = 'https://api.bitfinex.com'
        self.key = apikey
        self.secret = secret
        self.apiVersion = 'v1'
        self.symbols = []
        self.ticker = {}
        self.tickerTime = 0
        self.usedCurrencies = []
#        self.timeout = int(self.cfg.get("BOT", "timeout", 30, 1, 180))
        self.timeout = 180
        # Initialize usedCurrencies
        _ = self.return_available_account_balances("lending")

    @property
    def _nonce(self):
        '''
        Returns a nonce
        Used in authentication
        '''
        return str(int(round(time.time() * 1000)))

    def _sign_payload(self, payload):
        j = json.dumps(payload)
        data = base64.standard_b64encode(j.encode('utf8'))

        h = hmac.new(self.secret.encode('utf8'), data, hashlib.sha384)
        signature = h.hexdigest()
        return {
            "X-BFX-APIKEY": self.key,
            "X-BFX-SIGNATURE": signature,
            "X-BFX-PAYLOAD": data
        }

    def _request(self, method, request, payload=None, verify=True):
        try:
            r = {}
            url = '{}{}'.format(self.url, request)
            if (method == 'get'):
                r = requests.get(url, timeout=self.timeout)
            else:
                r = requests.post(url, headers=payload, verify=verify, timeout=self.timeout)

            if r.status_code != 200:
                if (r.status_code == 502 or r.status_code in range(520, 527, 1)):
                    raise ApiError('API Error ' + str(r.status_code) +
                                   ': The web server reported a bad gateway or gateway timeout error.')
                else:
                    raise ApiError('API Error ' + str(r.status_code) + ': ' + r.text)

            return r.json()

        except Exception as ex:
            ex.message = ex.message if ex.message else str(ex)
            ex.message = "{0} Requesting {1}".format(ex.message, self.url + request)
            raise ex

    def _post(self, command, payload=None, verify=True):
        payload = payload or {}
        payload['request'] = '/{}/{}'.format(self.apiVersion, command)
        payload['nonce'] = self._nonce
        signed_payload = self._sign_payload(payload)
        return self._request('post', payload['request'], signed_payload, verify)

    def _get(self, command):
        request = '/{}/{}'.format(self.apiVersion, command)
        return self._request('get', request)

    # def _getSymbols(self):
    #     '''
    #     A list of symbol names. Currently "btcusd", "ltcusd", "ltcbtc", ...
    #     https://bitfinex.readme.io/v1/reference#rest-public-symbols
    #     '''
    #     if len(self.symbols) == 0:
    #         bfxResp = self._get('symbols')
    #         allCurrencies = self.cfg.get_all_currencies()
    #         for symbol in bfxResp:
    #             base = symbol[3:].upper()
    #             curr = symbol[:3].upper()
    #             if base in ['USD', 'BTC'] and curr in allCurrencies:
    #                 self.symbols.append(symbol)

    #     return self.symbols

    def return_open_loan_offers(self):
        '''
        Returns active loan offers
        https://bitfinex.readme.io/v1/reference#rest-auth-offers
        '''
        bfxResp = self._post('offers')
#        resp = Bitfinex2Poloniex.convertOpenLoanOffers(bfxResp)

        return bfxResp

    def return_loan_orders(self, currency, limit=0):
        command = ('lendbook/' + currency + '?limit_asks=' + str(limit) + '&limit_bids=' + str(limit))
        bfxResp = self._get(command)
#        resp = Bitfinex2Poloniex.convertLoanOrders(bfxResp)

        return bfxResp

    def return_active_loans(self):
        '''
        Returns own active loan offers
        https://bitfinex.readme.io/v1/reference#rest-auth-offers
        '''
        bfxResp = self._post('credits')
#        resp = Bitfinex2Poloniex.convertActiveLoans(bfxResp)

        return bfxResp

    def return_ticker(self):
        '''
        The ticker is a high level overview of the state of the market
        https://bitfinex.readme.io/v1/reference#rest-public-ticker
        '''
        t = int(time.time())
        if (t - self.tickerTime < 60):
            return self.ticker

        setTickerTime = True

        for symbol in self._getSymbols():
            base = symbol[3:].upper()
            curr = symbol[:3].upper()
            if base in ['BTC', 'USD'] and (curr == 'BTC' or curr in self.usedCurrencies):
                couple = (base + '_' + curr)
                coupleReverse = (curr + '_' + base)

                try:
                    ticker = self._get('pubticker/' + symbol)

                    if 'message' in ticker:
                        raise ApiError("Error: {} ({})".format(ticker['message'], symbol))

                    self.ticker[couple] = {
                        "last": ticker['last_price'],
                        "lowestAsk": ticker['ask'],
                        "highestBid": ticker['bid'],
                        "percentChange": "",
                        "baseVolume": str(float(ticker['volume']) * float(ticker['mid'])),
                        "quoteVolume": ticker['volume']
                    }
                    self.ticker[coupleReverse] = {
                        "last": 1 / float(self.ticker[couple]['last']),
                        "lowestAsk": 1 / float(self.ticker[couple]['lowestAsk']),
                        "highestBid": 1 / float(self.ticker[couple]['highestBid'])
                    }

                except Exception as ex:
                    self.log.log_error('Error retrieving ticker for {}: {}. Continue with next currency.'
                                       .format(symbol, ex.message))
                    setTickerTime = False
                    continue

        if setTickerTime and len(self.ticker) > 2:  # USD_BTC and BTC_USD are always in
            self.tickerTime = t

        return self.ticker

    def return_available_account_balances(self, account):
        '''
        Returns own balances sorted by account
        https://bitfinex.readme.io/v1/reference#rest-auth-wallet-balances
        '''
        bfxResp = self._post('balances')
#        balances = Bitfinex2Poloniex.convertAccountBalances(bfxResp, account)

        if 'lending' in bfxResp:
            for curr in bfxResp['lending']:
                if curr not in self.usedCurrencies:
                    self.usedCurrencies.append(curr)

        return bfxResp

    def cancel_loan_offer(self, currency, order_number):
        '''
        Cancels an offer
        https://bitfinex.readme.io/v1/reference#rest-auth-cancel-offer
        '''
        payload = {
            "offer_id": order_number,
        }

        bfxResp = self._post('offer/cancel', payload)

        success = 0
        message = ''
        try:
            if bfxResp['id'] == order_number:
                success = 1
                message = "Loan offer canceled ({:.4f} @ {:.4f}%).".format(float(bfxResp['remaining_amount']),
                                                                           float(bfxResp['rate']) / 365)
        except Exception as e:
            message = "Error canceling offer: ", str(e)
            success = 0

        return {"success": success, "message": message}

    def create_loan_offer(self, currency, amount, duration, auto_renew, lending_rate):
        '''
        Creates a loan offer for a given currency.
        https://bitfinex.readme.io/v1/reference#rest-auth-new-offer
        '''

        payload = {
            "currency": currency,
            "amount": str(amount),
            "rate": str(lending_rate * 36500),
            "period": int(duration),
            "direction": "lend"
        }

        try:
            bfxResp = self._post('offer/new', payload)
            plxResp = {"success": 0, "message": "Error", "orderID": 0}
            if bfxResp['id']:
                plxResp['orderId'] = bfxResp['id']
                plxResp['success'] = 1
                plxResp['message'] = "Loan order placed."
            return plxResp

        except Exception as e:
                msg = str(e)
                # "Invalid offer: incorrect amount, minimum is 50 dollar or equivalent in USD"
                if "Invalid offer: incorrect amount, minimum is 50" in msg:
                    usd_min = 50
                    cur_min = usd_min
                    if currency != 'USD':
                        cur_min = usd_min / float(self.return_ticker()['USD_' + currency]['lowestAsk'])

                    raise Exception("Error create_loan_offer: Amount must be at least " + str(cur_min) + " " + currency)
                else:
                    raise e

    def return_balances(self):
        '''
        Returns balances of exchange wallet
        https://bitfinex.readme.io/v1/reference#rest-auth-wallet-balances
        '''
        balances = self.return_available_account_balances('exchange')
        return balances['exchange']

    def transfer_balance(self, currency, amount, from_account, to_account):
        '''
        Transfers values from one account/wallet to another
        https://bitfinex.readme.io/v1/reference#rest-auth-transfer-between-wallets
        '''
        accountMap = {
            'margin': 'trading',
            'lending': 'deposit',
            'exchange': 'exchange'
        }
        payload = {
            "currency": currency,
            "amount": amount,
            "walletfrom": accountMap[from_account],
            "walletto": accountMap[to_account]
        }

        bfxResp = self._post('transfer', payload)
        plxResp = {
            "status":  1 if bfxResp[0]['status'] == "success" else 0,
            "message": bfxResp[0]['message']
        }

        return plxResp