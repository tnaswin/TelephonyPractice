import logging
import inbound

from twisted.internet import protocol, reactor

from pyswitch import outbound
from inbound import calls

logging.basicConfig(level=logging.DEBUG, filename="outbound-example.log")


class OutboundProtocol(outbound.OutboundProtocol):

    def connectComplete(self, callinfo):
        self.myevents()
        print "****************************************************************"
        print callinfo
        uuid = callinfo['Unique-ID']
        self.getotp = calls[uuid]
        self.playback("/usr/local/freeswitch/sounds/\
                        en/us/callie/ivr/8000/ivr-hello.wav")
        self.playback("/usr/local/freeswitch/sounds/\
                        en/us/callie/ivr/8000/ivr-you_entered.wav")
        df = self.say(say_method="ITERATED", text= self.getotp.otp)
        df.addCallback(self.playbackOne)
        df.addErrback(self.playbackFailed)

    def playbackOne(self, digits):
        self.playback("/usr/local/freeswitch/sounds/\
                        en/us/callie/ivr/8000/ivr-you_entered.wav")
        df = self.say(say_method="ITERATED", text= self.getotp.otp)
        df.addCallback(self.playbackTwo)
        df.addErrback(self.playbackFailed)

    def playbackTwo(self, digits):
        self.playback("/usr/local/freeswitch/sounds/\
                        en/us/callie/ivr/8000/ivr-you_entered.wav")
        df = self.say(say_method="ITERATED", text= self.getotp.otp)
        df.addCallback(self.playbackComplete)
        df.addErrback(self.playbackFailed)

    def playbackComplete(self, digits):
        print "Playback complete", digits
        self.hangup()

    def playbackFailed(self, error):
        print "Playback failed", error
        self.hangup()


class Factory(protocol.ServerFactory):
    def __init__(self, calls=None):
        self.calls = calls
    protocol = OutboundProtocol

if __name__=="__main__":
    reactor.listenTCP(8085, Factory())
    inbound.webStart()
    reactor.run()
