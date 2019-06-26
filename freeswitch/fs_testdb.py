from pyswitch import outbound
from twisted.internet import protocol, reactor
import txdbinterface as txdb
import logging

logging.basicConfig(level=logging.DEBUG, filename="outbound-example.log")

class OutboundProtocol(outbound.OutboundProtocol):

    def connectComplete(self, callinfo):
        self.myevents()
        self.answer()
        df = self.playAndGetDigits(1, 1, 3, filename="/usr/local/freeswitch/\
                          sounds/en/us/callie/ivr/8000/ivr-you_entered.wav",
                          invalidfile='1000', varname="digits", regexp="\d")
        df.addCallback(self.playbackComplete)
        df.addErrback(self.playbackFailed)

    def playbackComplete(self, digits):
        print "Playback complete %s"%digits
        self.getUserFromDb(digits)

    def playbackFailed(self, error):
        print "Playback failed", error

    def getUserFromDb(self, digits):
        self.query = "select account from bank where id = %s" % digits
        print self.query
        df = txdb.execute(self.query)
        df.addCallback(self.onDb)
        df.addErrback(self.errDb)

    def onDb(self, result):
        print "result db"
        self.result = result[0]
        account_num = self.result["account"]
        print account_num
        if not result:
            return errDb(None)
        self.sayAccount(account_num)

    def errDb(self, error):
        print 'error db'
        print error

    def sayAccount(self, account_num):
        df = self.say(say_method="ITERATED", text=account_num)
        df.addBoth(self.onBoth)
        self.hangup()

    def onBoth(self, result):
        print 'Result. End.'
        print result
        self.hangup()


class Factory(protocol.ServerFactory):
    protocol = OutboundProtocol

if __name__=="__main__":
    reactor.listenTCP(8085, Factory())
    reactor.run()
