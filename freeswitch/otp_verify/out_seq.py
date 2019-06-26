import logging
import inbound

from twisted.internet import protocol, reactor
from starpy.fastagi import InSequence

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
        sequence = InSequence()
        sequence.append(self.playback("/usr/local/freeswitch/sounds/\
                        en/us/callie/ivr/8000/ivr-hello.wav"))
        sequence.append(self.playback("/usr/local/freeswitch/sounds/\
                        en/us/callie/ivr/8000/ivr-you_entered.wav"))
        sequence.append(self.say(say_method="ITERATED", text= self.getotp.otp))
        sequence.append(self.playback("/usr/local/freeswitch/sounds/\
                        en/us/callie/ivr/8000/ivr-you_entered.wav"))
        sequence.append(self.say(say_method="ITERATED", text= self.getotp.otp))
        sequence.append(self.playback("/usr/local/freeswitch/sounds/\
                        en/us/callie/ivr/8000/ivr-you_entered.wav"))
        sequence.append(self.say(say_method="ITERATED", text= self.getotp.otp))
        sequence.append(self.playback("/usr/local/freeswitch/sounds/\
                        en/us/callie/ivr/8000/ivr-thank_you.wav"))
        sequence.append(self.hangup())
        def playbackFailed(self, error):
            print "Playback failed", error
            self.hangup()
        return sequence().addErrback(playbackFailed)

class Factory(protocol.ServerFactory):
    def __init__(self, calls=None):
        self.calls = calls
    protocol = OutboundProtocol

if __name__=="__main__":
    reactor.listenTCP(8085, Factory())
    inbound.webStart()
    reactor.run()
