#!/usr/bin/python

import uuid
import cgi
import logging

from pyswitch import *

from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor

log = logging.getLogger("InboundTest")

calls = {}
IP = None

class Call():

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
        num = cgi.escape(request.args["mobile"][0])
        otp = cgi.escape(request.args["otp"][0])
        print num, otp
        c = Call(num,otp)
        IP.dial(c)
        return '''<html><body>You submitted: %s <br> Wait for OTP!</body>
                </html>''' % num


class InboundTest:

    def onLogin(self, protocol):
        log.info("successfully logged in")
        self.eventsocket = protocol
        df = self.eventsocket.subscribeEvents("all")
        df.addCallbacks(self.onEventsSucess, self.onEventsFailure)

    def onEventsSucess(self, event):
        log.info(event)
        global IP
        IP = self

    def dial(self, c):
        self.uid = str(uuid.uuid1())
        self.url = "sofia/internal/" + c.num + "%"
        df = self.eventsocket.apiOriginate(
             self.url, "socket", appargs = "127.0.0.1:8085",
             cidname="1000", cidnum="1000",
             channelvars={"origination_uuid":self.uid}, background=True)
        self.eventsocket.registerEvent("CHANNEL_STATE", False, self.channelState)
        self.eventsocket.registerEvent("CHANNEL_ANSWER", False, self.channelAnswer)
        df.addCallback(self.originateSuccess)
        calls[self.uid]=c

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


def webStart():
    root = Resource()
    root.putChild("form", FormPage())
    factory = Site(root)
    reactor.listenTCP(8880, factory)


logging.basicConfig(level = logging.DEBUG)

f = inbound.InboundFactory("ClueCon")
p = InboundTest()
f.loginDeferred.addCallback(p.onLogin)
f.loginDeferred.addErrback(p.onLoginFailed)
reactor.connectTCP("127.0.0.1", 8021, f)
