#!/usr/bin/python

import uuid
import cgi
import logging

from pyswitch import outbound
from pyswitch import *

from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import protocol, reactor

log = logging.getLogger("InboundTest")
logging.basicConfig(level=logging.DEBUG, filename="outbound-example.log")

calls = {}

class Call(self):

    def __init__(self, num, otp):
        self.num = num
        self.otp = otp

class FormPage(Resource):

    def render_GET(self, request):
        return '''
                <html><body>
                <form method="POST">
                Enter your mobile number: <input name="mobile" type="text" />
                Enter OTP: <input name="otp" type="text" />
                <button type="submit" value="Submit">Request OTP</button>
                </form>
                </body></html>'''

    def render_POST(self, request):
        self.mob = (cgi.escape(request.args["mobile"][0]),)
        self.otp = (cgi.escape(request.args["otp"][0]),)
        reactor.connectTCP("127.0.0.1", 8021, f)
        return '''<html><body>You submitted: %s <br> Wait for OTP!</body>
                </html>''' % (cgi.escape(request.args["mobile"][0]),)


class InboundTest:


    def onLogin(self, protocol):
        log.info("successfully logged in")
        self.eventsocket = protocol
        df = self.eventsocket.subscribeEvents("all")
        df.addCallbacks(self.onEventsSucess, self.onEventsFailure)

    def onEventsSucess(self, event):
        log.info(event)
        self.uid = str(uuid.uuid1())
        self.url = "sofia/internal/1000%"
        df = self.eventsocket.apiOriginate(
        self.url, "socket", appargs = "127.0.0.1:8085",  cidname="1000", cidnum="1000" ,
        channelvars={"origination_uuid":self.uid},  background=True)
        self.eventsocket.registerEvent("CHANNEL_STATE", False, self.channelState)
        self.eventsocket.registerEvent("CHANNEL_ANSWER", False, self.channelAnswer)
        df.addCallback(self.originateSuccess)

    def originateSuccess(self, event):
        print "originate success"
        print event

    def channelState(self, event):
        print "channel state"

    def channelAnswer(self, event):
        print "channel answer"

    def onEventsFailure(self, error):
        print error

    def onGlobalGetVar(self, var):
        log.info(var)

    def onLoginFailed(self, error):
        log.error("Login failed")
        log.error(error)


class OutboundProtocol(outbound.OutboundProtocol):

    def connectComplete(self, callinfo):
        self.myevents()
        #self.answer()
        df = self.say(say_method="ITERATED", text= "12345")
        #=self.say(say_method="PRONOUNCED", text="Hello World")
        df.addCallback(self.playbackComplete)
        df.addErrback(self.playbackFailed)

    def playbackComplete(self, digits):
        print "Playback complete %s"%digits
        self.hangup()

    def playbackFailed(self, error):
        print "Playback failed", error
        self.hangup()

class Factory(protocol.ServerFactory):
    protocol = OutboundProtocol


logging.basicConfig(level = logging.DEBUG)


f = inbound.InboundFactory("ClueCon")
p = InboundTest()
f.loginDeferred.addCallback(p.onLogin)
f.loginDeferred.addErrback(p.onLoginFailed)

if __name__=="__main__":
    root = Resource()
    root.putChild("form", FormPage())
    factory = Site(root)
    reactor.listenTCP(8880, factory)
    reactor.run()
