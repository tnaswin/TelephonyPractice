#! /usr/bin/python

import sys
import time
import logging

from starpy import manager
from twisted.internet import reactor

extension = 0   # Takes the dialed extension
cdr = 0         # Stores the Call Details Record
ami = None      # Stores the AMIProtocol
start = 0       # Get the call answer time
end = 0         # Get the call Hangup time

def main():
    """Asterisk Manager Interface Login"""
    print("Main")
    f = manager.AMIFactory('aswin', '12345678')
    df = f.login(ip='192.168.5.86')
    df.addCallbacks(on_login, on_failure)
    return df

def on_login(protocol):
    """On Login, attempt to originate the call"""
    global ami
    ami = protocol
    print("On Login")
    channel='sip/'+extension
    context, exten, priority, timeout = 'phones', '1111', '1', 5
    ami.events(eventmask = 'on')
    ami.registerEvent('BridgeCreate', on_bridge)
    ami.registerEvent('Hangup', on_channel_hangup)
    ami.registerEvent("Cdr", on_cdr)
    df = ami.originate(channel, context,
                            exten, priority, timeout)
    df.addCallback(on_finished)
    df.addErrback(on_failure)
    return df

def on_finished(result):
    print("On Finish")
    print(result)
    #uniqueChannelId = agi.variables['agi_uniqueid']
    df = ami.status()
    return df.addCallbacks(on_status, on_failure)

def on_status(details):
    "Get the Call Details Record"
    global cdr
    cdr = details
    print("On Status")
    print(cdr)

def on_bridge(*args):
    """On Bridge Create event get timestamp"""
    print("Bridge")
    print(args)
    global start
    start = time.time()

def on_channel_hangup(ami, event):
    """Hangup of an event"""
    if event['uniqueid'] in [d['uniqueid'] for d in cdr if 'uniqueid' in d]:
        print("Channel Hangup")
        print event
        print("uniqueid", event['uniqueid'])
        global end
        end = time.time()
        reactor.callLater(1, df.callback, event)
        ami.deregisterEvent('Hangup', on_channel_hangup)

def on_cdr(ami, event):
    "Get the Call detail record using cdr event"
    print("Call Detail Record: ")
    for k,v in event.items():
        print("%s == %s" % (k, v))

def on_failure(reason):
    """Unable to log in!"""
    print(reason.getTraceback())
    #hangup()

def call(ext):
    global extension
    extension = ext
    manager.log.setLevel(logging.DEBUG)
    logging.basicConfig()
    reactor.callWhenRunning(main)
