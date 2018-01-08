from django.shortcuts import render
from django.views.generic import TemplateView
from django.shortcuts import *
from app.models import *
from app.markets.Bittrex import *
from app.markets.Poloniex import *
from app.markets.GDAX import *
from app.markets.Gemini import *
from app.markets.Kraken import *
from binance.client import BinanceRESTAPI

from django.http import HttpResponse
import time
import datetime
import threading
import subprocess
import psutil
import requests

# bapikey = "9014051c35c7433db70f16de0cd24fd2"
# bsecret = "af5c0efdf58347e49707b3f2cac8867c"

# papikey = "REM9I16W-5YZV3O5L-080GYOCA-VKWFT99B"
# psecret = "b5403a9845ef42639b9a4a376a80f17e285af5c8a5f89259fdc34515bdcb4409bb98517bc622dd2f946c5fcb2e0557cdffc9b95211a7306517936f71b5007d7d"

# gapikey = "603e48e47b3f2a184c5cca86049ffa53"
# gapisecret = "a7KOEF3QmRQ/TKP8GwfyMIwgyi649om84Tv5y/N/F6S1hKWrkTJUagbjwJHq86+xbcGLT4iKCgpQvdrMkl7MIg=="
# gapipass = "jeboyoaazpl"

# geminikey = "qApEwFoL2qztTiCkkOAh"
# geminisecret = "oXAfpFaGaW7k7rv7YezJ9RN9SnV"

# krakenkey = "A5Ra1NSZ4LG7NjEpq2XRPyJSVZjyc0JqFqt3A6NSugvlMwcbchmnmID8"
# krakensecret = "uDP0fH9dWopb5sdynJ2GgPDBvBSihgyXUItDZs2jh6jRv/vJEP1f7leLZQ8Q3fxSNRXbVuIxKHtgCwu4NjQdNw=="

# bittrexApi = Bittrex(bapikey, bsecret)
# poloniexapi = Poloniex(papikey, psecret)
# gdaxApi = gdax(gapikey, gapisecret, gapipass)
# geminiApi = Gemini(geminikey, geminisecret, True)
# krakenApi = Kraken(krakenkey, krakensecret)

binanceKey = "QWQKiAhvI3z6jV3wWHcBhjkW3aqtfikGnTsItvmKVeND7nQtuNxVePysYJ1qECDx"
#binanceKey = "rqNAeUd6OodEOMz2lH2KZfYP0mRbRwt6uchJUeWwKq9ZAmRPCzgHIiFpSD8DFWYi"
binanceSecret = "hy4ztpnKH1YlfQDCE3L2BoA4Tsz1cE4a3jRzYR0hzCkClF71IAbZETbBjjvku515"
#binanceSecret = "67JhwejUWyKe7QbmxIC5i2BNQQnrHhJQCwr3pcXR39EqcLLToyQ0t0cSHFi7FGWi"
binance_rest_client = BinanceRESTAPI(binanceKey, binanceSecret)

bShowAll = False
procId = 0
        
def accountInfo_read(request, **kwargs):

    error = kwargs['error'] if len(kwargs)>0 else ""
    
    balanceArray = []
    depth = binance_rest_client.depth("BTCUSDT")

    # total voulme
    totalVolume = depth.get_depth_volume()

    # best bid price
    highestPrice = depth.get_bids_highest_price()

    # best ask price
    lowestPrice = depth.get_asks_lowest_price()

    print(totalVolume)
    print(highestPrice)
    print(lowestPrice)

    account = binance_rest_client.account()
    btcBalance = 0
# balance information
    for balance in account.balances:
        if ( balance.asset == "BTC" ):
            btcBalance = balance.free
            print(balance.free)
            print(balance.locked)

    coinData = {
        'coinName': "BTC",
        'balance': btcBalance,
        'highestPrice': highestPrice,
        'lowestPrice': lowestPrice,
        'currentvalue': 0,
        'unrealized': 0,
        'realized': 0
    }

    balanceArray.insert(len(balanceArray), coinData)

    depth = binance_rest_client.depth("ETHUSDT")

    # total voulme
    totalVolume = depth.get_depth_volume()

    # best bid price
    highestPrice = depth.get_bids_highest_price()

    # best ask price
    lowestPrice = depth.get_asks_lowest_price()

    print(totalVolume)
    print(highestPrice)
    print(lowestPrice)

    account = binance_rest_client.account()
    ethBalance = 0
# balance information
    for balance in account.balances:
        if ( balance.asset == "BTC" ):
            btcBalance = balance.free
            print(balance.free)
            print(balance.locked)

    coinData = {
        'coinName': "ETH",
        'balance': ethBalance,
        'highestPrice': highestPrice,
        'lowestPrice': lowestPrice,
        'currentvalue': 0,
        'unrealized': 0,
        'realized': 0
    }

    balanceArray.insert(len(balanceArray), coinData)

#    gdaxApi.place_limit_order('buy', 'BTC-USD', 2000, 1 )
#    gdaxApi.cancel_order_all()
#     for bal in balance1['result']:
#         try:
#             market = ''
#             currentprice = 0
#             marketBidPrice = 0
#             marketAskPrice = 0
#             refPrice = 0

# #            ticker_response = bittrexApi.get_ticker(unicode('USDT-'+bal['Currency']))
# #            if ( ticker_response['success'] == False ):
#             ticker_response = bittrexApi.get_ticker(unicode('BTC-'+bal['Currency']))
#             if ( ticker_response['success'] == False ):
#                 ticker_response = bittrexApi.get_ticker(unicode('ETH-'+bal['Currency']))
#                 if ( ticker_response['success'] == True ):
#                     currentprice = ticker_response['result']['Bid'] * currentETHPrice
#                     marketBidPrice = ticker_response['result']['Bid']
#                     marketAskPrice = ticker_response['result']['Ask']
#                     refPrice = currentETHPrice
#                     market = 'ETH-'
#             else:
#                 currentprice = ticker_response['result']['Bid']
# #                currentprice = ticker_response['result']['Bid'] * currentBTCPrice
#                 marketBidPrice = ticker_response['result']['Bid']
#                 marketAskPrice = ticker_response['result']['Ask']
#                 refPrice = currentBTCPrice
#                 market = 'BTC-'
#             # else:
#             #     currentprice = ticker_response['result']['Bid']
#             #     marketBidPrice = ticker_response['result']['Bid']
#             #     marketAskPrice = ticker_response['result']['Ask']
#             #     refPrice = 1
#             #     market = 'USDT-'
            
#             coinData = {
#                 'coinName': bal['Currency'],
#                 'coinAmount': bal['Balance'],
#                 'BittrexPrice': currentBTCPrice,
#                 'PoloniexPrice': currentBTCPrice_polo,
#                 'Difference': float(currentBTCPrice) - float(currentBTCPrice_polo),
#                 'cost': refPrice,
#                 'currentvalue': market + bal['Currency'],
#                 'unrealized': marketAskPrice,
#                 'realized': marketBidPrice
#             }

#             if ( bal['Balance'] != 0 ):
#                 print(market + bal['Currency'])
#                 orderHistory = bittrexApi.get_order_history(unicode(market + bal['Currency']))['result']
                
#                 if ( orderHistory != [] ):
#                     temp_cost = 0
#                     temp_quantity = 0
#                     temp_price = 0
#                     for trans in orderHistory:
#                         print(trans)
#                         if ( trans['OrderType'] == 'LIMIT_BUY' ):
# #                            temp_cost +=  trans['PricePerUnit'] * trans['Quantity'] * refPrice
#                             temp_cost +=  trans['PricePerUnit'] * trans['Quantity']
#                             temp_quantity += trans['Quantity']
#                         elif ( trans['OrderType'] == 'LIMIT_SELL' ):
# #                            temp_cost -= trans['PricePerUnit'] * trans['Quantity'] * refPrice
#                             temp_cost -= trans['PricePerUnit'] * trans['Quantity']
#                             temp_quantity -= trans['Quantity']

#                     print(temp_cost)
#                     print(temp_quantity)
#                     coinData['costperunit'] = temp_cost / temp_quantity
#                     coinData['change'] = (currentprice - coinData['costperunit']) / coinData['costperunit']  * 100
            
# #            balanceArray.insert(len(balanceArray), coinData)
#             balanceArray.insert(len(balanceArray), coinData)
#             break
#         except Exception, e:
#             pass
# #            print(coinData)
        
        

    return render(request, 'arbitrage/arbitrage.html', {
        'error': error,
        'balances': balanceArray,
        'bShowAll': bShowAll,
    })

def show_all_coin(request):
    global bShowAll
    bShowAll = True
    return HttpResponse("SHOW")

def hide_zero_amount(request):
    global bShowAll
    bShowAll = False
    return HttpResponse("HIDE")

def start_bot(request):
    
    # global procId    
    if (request.method == 'GET'):
        divNumber = int(request.GET['divNumber'])
        print(divNumber)
        stepPercent = float(request.GET['stepPercent'])
        
        print(stepPercent)

        account = binance_rest_client.account()
        btcBalance = 0
    # balance information
        for balance in account.balances:
#            if ( balance.asset == "BTC" ):
            if ( balance.asset == request.GET['coin']):
                btcBalance = balance.free
                print(balance.free)
                print(balance.locked)
            elif ( balance.asset == 'USDT' ):
                print(balance.free)
                print(balance.locked)
        
        if ( request.GET['side'] == 'sell' ):
            highestPrice = request.GET['sellHighestPrice']
            print(highestPrice)
            priceStep = float(float(highestPrice) / 100 * stepPercent)
            print(priceStep)
            i = 0
            while i < divNumber:
                print(i)
                sellPrice = float(highestPrice) + 3000 - float(priceStep) * float(i)
                sellAmount = float(btcBalance) / float(divNumber)
                sellPrice = format(sellPrice, '.2f')
                sellAmount = format(sellAmount, '.6f')
                try:
                    order = binance_rest_client.new_order(request.GET['coin'] + "USDT", "SELL", "LIMIT", "GTC", sellAmount, sellPrice)

                    print order, type(order)
                except Exception, e:
                    print e

                i = i + 1
        
        if ( request.GET['side'] == 'buy' ):
            lowestPrice = request.GET['buyLowestPrice']
            print(lowestPrice)
            priceStep = float(float(lowestPrice) / 100 * stepPercent)
            print(priceStep)
            i = 0
            while i < divNumber:
                print(i)
                buyPrice = float(lowestPrice) - 3000 + float(priceStep) * float(i)
                buyAmount = float(btcBalance) / float(divNumber)
                buyPrice = format(buyPrice, '.2f')
                buyAmount = format(buyAmount, '.6f')
                try:
                    order = binance_rest_client.new_order(request.GET['coin'] + "USDT", "BUY", "LIMIT", "GTC", buyAmount, buyPrice)

                    print order
                except Exception, e:
                    print e

                i = i + 1

#        order = binance_rest_client.new_order_test("BTCUSDT", "SELL", "LIMIT", "GTC", 0.01, highestPrice + 1000)

    # proc = subprocess.Popen(["python", "/Volumes/Backup/workspace/Nir(Arbitrage)/cryptocurrency_arbitrage/Arbitrage.py", tollerance, amount])
    # procId = proc.pid
    # print(procId)
    # print("start_bot")
    return HttpResponse("Start")

def stop_bot(request):
    # print(procId)
    # if psutil.pid_exists(procId):
    #     p = psutil.Process(procId)
    #     p.terminate()
    # print("stop_bot")
    print("OKOK")
    account = binance_rest_client.account()
    btcBalance = 0
# balance information
    for balance in account.balances:
        if ( balance.asset == request.GET['coin'] ):
            btcBalance = balance.free
            print(balance.free)
            print(balance.locked)
    # payload = {"apiKey": "vmPUZE6mv9SD5VNHk4HlWFsOr6aKE2zvsw0MuIgwCIPy6utIco14y7Ju91duEh8A",
    #             "secretKey": "NhqPtmdSJYdKjVHjA7PZj4Mge3R5YNiP1e3UZjInClVN65XAbvqqM6A7H5fATj0j"}
    # r = requests.get("https://www.binance.com/api/v3/openOrders", params=payload)
    # print(r)
    print "================="
    orders = binance_rest_client.current_open_orders(symbol=request.GET['coin'] + "USDT", recvWindow=6000000)
    print orders
    print "========"
    # orders = binance_rest_client.all_orders(symbol="BTCUSDT")
    # print orders

    
    for order in orders:
        if order.status == "NEW":
            print type(order), "=", order.id, "=", order.status, "=", order.side
            order = binance_rest_client.cancel_order(request.GET['coin'] + "USDT", order.id)
    return HttpResponse("Stop")

def set_api(request):
    global binance_rest_client
    print("SET_API")
    if (request.method == 'GET'):
        print(request.GET)
        binance_rest_client = BinanceRESTAPI(request.GET['key'], request.GET['secret'])
    return HttpResponse("setAPI")
