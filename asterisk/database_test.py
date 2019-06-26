#! /usr/bin/python
from twisted.internet import reactor
from starpy import fastagi
import txdbinterface as txdb
import logging


log = logging.getLogger('database_test')

agi = None

def testFunction(agi_return):
    global agi
    agi = agi_return
    log.debug('testFunction')
    df = agi.getData(filename='hello-world',maxDigits=1)
    df.addCallback(onGetData)
    df.addErrback(errGetData)

def onGetData(result):
    print("In getData")
    print(result)
    if not result:
        return errGetData()
    user_id = result[0]
    return getUserFromDb(user_id)

def getUserFromDb(user_id):
    query = "select account from bank where id = %s" % user_id
    print query
    df = txdb.execute(query)
    df.addCallback(onDb)
    df.addErrback(errDb)

def errGetData(error=None):
    print("Error in get data")
    print(error)

def onDb(result):
    print("result db")
    result = result[0]
    account_num = result["account"]
    print account_num
    print(result)
    if not result:
        return errDb(None)
    sayAccount(account_num)

def errDb(error):
    print('error db')
    print(error)

def sayAccount(account_num):
    global agi
    sequence = fastagi.InSequence()
    sequence.append(agi.sayDigits, account_num)
    sequence.append(agi.finish)
    sequence().addBoth(onFailure)

def onFailure(reason):
    global agi
    log.error("Failure: %s", reason.getTraceback())
    agi.finish()

if __name__ == "__main__":
    logging.basicConfig()
    fastagi.log.setLevel(logging.DEBUG)
    f = fastagi.FastAGIFactory(testFunction)
    reactor.listenTCP(4573, f, 50, '127.0.0.1')
    reactor.run()
