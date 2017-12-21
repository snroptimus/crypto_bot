#from app.markets.Bittrex import *
#from app.markets.Poloniex import *
from app.markets.GDAX import *
from app.markets.Gemini import *
from app.markets.Kraken import *

import time
import datetime
import string
import random
import argparse
import os
import sys
import json
import urllib2


bapikey = "9014051c35c7433db70f16de0cd24fd2"
bsecret = "af5c0efdf58347e49707b3f2cac8867c"

papikey = "REM9I16W-5YZV3O5L-080GYOCA-VKWFT99B"
psecret = "b5403a9845ef42639b9a4a376a80f17e285af5c8a5f89259fdc34515bdcb4409bb98517bc622dd2f946c5fcb2e0557cdffc9b95211a7306517936f71b5007d7d"

gapikey = "603e48e47b3f2a184c5cca86049ffa53"
gapisecret = "a7KOEF3QmRQ/TKP8GwfyMIwgyi649om84Tv5y/N/F6S1hKWrkTJUagbjwJHq86+xbcGLT4iKCgpQvdrMkl7MIg=="
gapipass = "jeboyoaazpl"

geminikey = "qApEwFoL2qztTiCkkOAh"
geminisecret = "oXAfpFaGaW7k7rv7YezJ9RN9SnV"

krakenkey = "A5Ra1NSZ4LG7NjEpq2XRPyJSVZjyc0JqFqt3A6NSugvlMwcbchmnmID8"
krakensecret = "uDP0fH9dWopb5sdynJ2GgPDBvBSihgyXUItDZs2jh6jRv/vJEP1f7leLZQ8Q3fxSNRXbVuIxKHtgCwu4NjQdNw=="

# bittrexApi = Bittrex(bapikey, bsecret)
# poloniexapi = Poloniex(papikey, psecret)


gapikey = ""
gapisecret = ""
gapipass = ""

geminikey = ""
geminisecret = ""

krakenkey = ""
krakensecret = ""

gapikey = str(sys.argv[1])
gapisecret = str(sys.argv[2])
gapipass = str(sys.argv[3])

geminikey = str(sys.argv[4])
geminisecret = str(sys.argv[5])

krakenkey = str(sys.argv[6])
krakensecret = str(sys.argv[7])


tollerance = float(sys.argv[8])
amount = float(sys.argv[9])

useKraken = bool(sys.argv[10] == "true")
useGemini = bool(sys.argv[11] == "true")
useGdax = bool(sys.argv[12] == "true")

print(useKraken)
print(useGemini)
print(useGdax)

feeKraken = float(sys.argv[13])
feeGemini = float(sys.argv[14])
feeGdax = float(sys.argv[15])

runInterval = float(sys.argv[16])

testMode = bool(sys.argv[17] == "true")
opportunity = float(sys.argv[18])

print("TEST")
print(testMode)
print(feeKraken)
print(feeGemini)
print(feeGdax)

gdaxApi = gdax(gapikey, gapisecret, gapipass)
geminiApi = Gemini(geminikey, geminisecret, False)
krakenApi = Kraken(krakenkey, krakensecret)

print(tollerance)
print(amount)

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


apiArray = []
nameArray = []
feeArray = []
if ( useKraken ):
    apiArray.insert(0, krakenApi)
    nameArray.insert(0, "Kraken")
    feeArray.insert(0, feeKraken)
if ( useGemini ):
    apiArray.insert(0, geminiApi)
    nameArray.insert(0, "Gemini")
    feeArray.insert(0, feeGemini)
    
if ( useGdax ):
    apiArray.insert(0, gdaxApi)
    feeArray.insert(0, feeGdax)
    nameArray.insert(0, "Gdax")

def arbitrage():
    priceArray = []
    geminiBTCprice = float(geminiApi.get_ticker('btcusd')['last'])
    gdaxBTCprice = (float)(gdaxApi.get_ticker('BTC-USD')['price'])
    krakenBTCprice = float(krakenApi.get_ticker('XXBTZUSD')[0])
    
    if ( useKraken ):
        priceArray.insert(0, krakenBTCprice)
    if ( useGemini ):
        priceArray.insert(2, geminiBTCprice)    
    if ( useGdax ):
        priceArray.insert(1, gdaxBTCprice)
    
    maxPrice = max(priceArray)
    maxIndex = priceArray.index(maxPrice)
    minPrice = min(priceArray)
    minIndex = priceArray.index(minPrice)

    print(priceArray)
    print(maxIndex)
    print(minIndex)

    threshold = minPrice / 100 * tollerance
    print(threshold)

    minAmount = minPrice * amount
    maxAmount = maxPrice * amount
    delte = maxPrice - minPrice
    avgPrice = (maxPrice + minPrice) / 2
    fee = feeArray[maxIndex] + feeArray[minIndex]
    profit = (delte / avgPrice) * 100

    print(delte)
    print(avgPrice)
    print(profit)
    print("opp")
    print(opportunity)

    if ( profit - fee > opportunity ):

        ts = time.time()
        print("date:" + datetime.datetime.fromtimestamp(ts).strftime('%a %b %d %Y %X %z'))
        print(nameArray[maxIndex] + ":" + str(maxPrice) + ", " + nameArray[minIndex] + ":" + str(minPrice))
        print(nameArray[minIndex] + " Order: Buy, BTC-USD, " + "price:" + str(minPrice + threshold) + ", amount:" + str(amount))
        print(nameArray[maxIndex] + " Order: Sell, BTC-USD, " + "price:" + str(maxPrice - threshold) + ", amount:" + str(amount))
        print("Profit:" + str((maxPrice-threshold - minPrice - threshold) * amount))
        print("----------------------------------------")
        
        # ts = time.time()
        f = open('./orderlist.json', 'a')
        f.write("{\"data\":")
        f.write("\"")
        f.write(datetime.datetime.fromtimestamp(ts).strftime('%a %b %d %Y %X&%z'))
        f.write(nameArray[maxIndex] + ":" + str(maxPrice) + "&" + nameArray[minIndex] + ":" + str(minPrice) + "&")
        f.write(str(maxPrice - minPrice) + "&")
        f.write(str(amount) + "&")
        f.write(str((maxPrice-threshold - minPrice - threshold) / ((maxPrice + minPrice) / 2) * 100 ) + "&")
        f.write(str((maxPrice-threshold - minPrice - threshold) / ((maxPrice + minPrice) / 2) * 100 - feeArray[maxIndex] - feeArray[minIndex]) + "&")
        f.write(str((maxPrice-threshold - minPrice - threshold) * amount) )
        f.write("\"}, ")
        f.close()

        if ( testMode ):
            print("TEST")
        else:
            if ( maxIndex == 2 ):
                pass
            elif ( maxIndex == 1 ):
#               geminiBalance = geminiApi.get_balance()
#               if ( geminiBalance['BTC'] > amount ):
                geminiApi.new_order(unicode(id_generator()), 'btcusd', amount, geminiBTCprice - threshold, 'sell', 'exchange limit')
            elif ( maxIndex == 0 ):
                # gdaxBalance = gdaxApi.get_balances()
                # if ( geminiBalance['BTC'] > amount):
                gdaxApi.place_limit_order('sell', 'BTC-USD', gdaxBTCprice - threshold, amount )

            if ( maxIndex == 2 ):
                pass
            elif ( maxIndex == 1 ):
#               geminiBalance = geminiApi.get_balance()
#               if ( geminiBalance['USD'] > amount * (geminiBTCprice + threshold)):
                geminiApi.new_order(unicode(id_generator()), 'btcusd', amount, geminiBTCprice + threshold, 'buy', 'exchange limit')
            elif ( maxIndex == 0 ):
                # gdaxBalance = gdaxApi.get_balances()
                # if ( geminiBalance['USD'] > amount * (gdaxBTCprice + threshold)):
                gdaxApi.place_limit_order('buy', 'BTC-USD', gdaxBTCprice + threshold, amount )

    '''
    if ( geminiBTCprice > gdaxBTCprice ):

        threshold = gdaxBTCprice / 100 * tollerance
        print(threshold)
        
        if ( geminiBTCprice - gdaxBTCprice > threshold * 2 ):

            ts = time.time()
            print("date:" + datetime.datetime.fromtimestamp(ts).strftime('%a %b %d %Y %X %z'))
            print("GeminiPrice:" + str(geminiBTCprice) + ", GDaxPrice" + str(gdaxBTCprice))
            print("GDax Order: Buy, BTC-USD, " + "price:" + str(gdaxBTCprice + threshold) + ", amount:" + str(amount))
            print("Gemini Order: Sell, BTC-USD, " + "price:" + str(geminiBTCprice - threshold) + ", amount:" + str(amount))
            print("Profit:" + str((geminiBTCprice-threshold - gdaxBTCprice - threshold) * amount))
            print("----------------------------------------")
            
            # ts = time.time()
            f = open('./orderlist.json', 'a')
            f.write("date:" + datetime.datetime.fromtimestamp(ts).strftime('%a %b %d %Y %X %z'))
            f.write("\n")
            f.write("GeminiPrice:" + str(geminiBTCprice) + ", GDaxPrice" + str(gdaxBTCprice))
            f.write("\n")
            f.write("GDax Order: Buy, BTC-USD, " + "price:" + str(gdaxBTCprice + threshold) + ", amount:" + str(amount))
            f.write("\n")
            f.write("Gemini Order: Sell, BTC-USD, " + "price:" + str(geminiBTCprice - threshold) + ", amount:" + str(amount))
            f.write("\n")
            f.write("Profit:" + str((geminiBTCprice - threshold - gdaxBTCprice - threshold) * amount))
            f.write("\n")
            f.write("----------------------------------------")
            f.write("\n")
            f.write("\n")
            f.close()
#            gdaxApi.place_limit_order('buy', 'BTC-USD', gdaxBTCprice + threshold, amount )
#            geminiApi.new_order(unicode(id_generator()), 'btcusd', amount, geminiBTCprice - threshold, 'sell', 'exchange limit')
    else:

        threshold = geminiBTCprice / 100 * tollerance
        print(threshold)
        
        if ( gdaxBTCprice - geminiBTCprice > threshold *2):
            ts = time.time()
            print("date:" + datetime.datetime.fromtimestamp(ts).strftime('%a %b %d %Y %X %z'))
            print("GeminiPrice:" + str(geminiBTCprice) + ", GDaxPrice" + str(gdaxBTCprice))
            print("Gemini Order: Buy, BTC-USD, " + "price:" + str(geminiBTCprice + threshold) + ", amount:" + str(amount))
            print("GDax Order: Sell, BTC-USD, " + "price:" + str(gdaxBTCprice - threshold) + ", amount:" + str(amount))
            print("Profit:" + str((gdaxBTCprice-threshold - geminiBTCprice - threshold) * amount))
            print("----------------------------------------")

            f = open('./orderlist.json', 'a')
            f.write("date:" + datetime.datetime.fromtimestamp(ts).strftime('%a %b %d %Y %X %z'))
            f.write("\n")
            f.write("GeminiPrice:" + str(geminiBTCprice) + ", GDaxPrice" + str(gdaxBTCprice))
            f.write("\n")
            f.write("GDax Order: Buy, BTC-USD, " + "price:" + str(geminiBTCprice + threshold) + ", amount:" + str(amount))
            f.write("\n")
            f.write("Gemini Order: Sell, BTC-USD, " + "price:" + str(gdaxBTCprice - threshold) + ", amount:" + str(amount))
            f.write("\n")
            f.write("Profit:" + str((gdaxBTCprice - threshold - geminiBTCprice - threshold) * amount))
            f.write("\n")
            f.write("----------------------------------------")
            f.write("\n")
            f.write("\n")
            f.close()
#            gdaxApi.place_limit_order('sell', 'BTC-USD', gdaxBTCprice - threshold, amount )
#            geminiApi.new_order(unicode(id_generator()), 'btcusd', amount, geminiBTCprice + threshold, 'buy', 'exchange limit')
    '''

def getBotInfo():
    pass

while True:
    getBotInfo()
    arbitrage()
    print
    if ( runInterval == 0 ):
        time.sleep(10)
    else:
        time.sleep(runInterval*60)