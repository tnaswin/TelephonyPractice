#! /usr/bin/python

import sys
import uuid
import datetime
import logging

import txdbinterface as txdb

from starpy import manager
from twisted.internet import reactor

temp = 0        # Temporary Flag
extension = 0   # Takes the dialed extension.
phone = 0       # Takes the caller phone number.
cdr = 0         # Stores the Call Status Details.
ami = None      # Stores the AMIProtocol.
start = 0       # Call start time.
uid = 0         # Unique ID
uid1 = 0        # Unique ID of leg A.
uid2 = 0        # Unique ID of leg B.
path = None     # Address of the recording file.
call_details = {}    #Dictionary to store required call details after hangup.


class OnCall():
    """Class to perform Call opertaions"""

    def __init__(self):
        self.channel='sip/' + phone
        self.context = None
        self.exten = None
        self.priority = None
        self.timeout = None
        self.start = None
        self.answer = None
        self.end = None
        self.duration = None
        self.disposition = "NOT ANSWERED"
        self.uniqueid = None

    def main(self):
        """Asterisk Manager Interface Login"""
        print("Main")
        f = manager.AMIFactory('aswin', '12345678')
        df = f.login(ip='192.168.5.86')
        df.addCallbacks(self.on_login, self.on_failure)
        return df

    def on_login(self, protocol):
        """On Login, attempt to originate the call"""
        global ami, uid
        ami = protocol
        print("On Login")
        uid = str(uuid.uuid1())
        print uid
        self.context, self.exten = 'clicktocall', extension
        self.priority, self.timeout = '1', 5
        ami.events(eventmask = 'on')
        ami.registerEvent('BridgeCreate', self.on_bridge)
        ami.registerEvent('Hangup', self.on_channel_hangup)
        df = ami.originate(self.channel, self.context,
                                self.exten, self.priority, self.timeout)
        df.addCallback(self.on_call)
        df.addErrback(self.on_failure)
        return df

    def on_call(self, result):
        """On AMI Originate"""
        print("On Finish")
        print(result)
        global start, path
        start = datetime.datetime.now()
        self.start = start.strftime('%H:%M:%S')
        self.path = start.strftime('%Y %b %d').split()
        path1 = "/opt/recordings/inbound/"
        path2 = self.path[0]+"/"+self.path[1]+"/"+self.path[2]+"/"
        file_name = "-"+self.exten+"-"+start.strftime('%H-%M-%S')+".gsm"
        path = path1 + path2 + file_name
        print (path)
        print(start)
        df = ami.status()
        return df.addCallbacks(self.on_status, self.on_failure)

    def on_status(self, details):
        "Get the Call Details Record"
        global cdr
        cdr = details
        print("On Status")
        print(cdr)

    def on_bridge(self, *args):
        """On Bridge Create event get timestamp"""
        print("Bridge")
        self.disposition = "ANSWERED"
        print(args)
        self.answer = datetime.datetime.now()
        self.answer = self.answer.strftime('%H:%M:%S')
        print(self.answer)

    def on_channel_hangup(self, ami, event):
        """Hangup of an event"""
        if event['uniqueid'] in [d['uniqueid'] for d in cdr if 'uniqueid' in d]:
            global uid1, uid2, call_details
            uid1 = event['uniqueid']
            uid2 = event['linkedid']
            print("Channel Hangup")
            print(event)
            self.uniqueid = event['uniqueid']
            print("uniqueid", event['uniqueid'])
            self.end = datetime.datetime.now()
            self.end = self.end.strftime('%H:%M:%S')
            fmt = '%H:%M:%S'
            if not self.answer:
                self.duration = 0
            else:
                self.duration = (datetime.datetime.strptime(self.end, fmt)
                                - datetime.datetime.strptime(self.answer, fmt))
            call_details = {'context':self.context, 'extension':self.exten,
                            'duration':self.duration,
                            'disposition':self.disposition,
                            'uniqueid':uid}
            global temp
            if temp == 0:
                print("INSIDE IF")
                temp = 1
                self.insert_into_db(event)
            else:
                temp = 0
                print("INSIDE ELSE")
                ami.deregisterEvent('Hangup', on_channel_hangup)

    def insert_into_db(self, event):
        print(call_details)
        query = """insert into cdrdb (calldate, recording, dst, dcontext,
                                      channel, dstchannel, lastapp, duration,
                                      disposition, uniqueid)
                   values ('%s', '%s', '%s', '%s', '%s', '%s',
                           '%s', '%s', '%s', '%s')""" %(
                   start, path, call_details['extension'],
                   call_details['context'], cdr[1].get('channel'),
                   cdr[2].get('channel'), cdr[1].get('application'),
                   call_details['duration'], call_details['disposition'],
                   call_details['uniqueid'])
        print(query)
        df = txdb.execute(query)
        df.addCallback(self.on_finish)
        df.addErrback(self.err_db)

    def on_finish(self, result):
        print("On Finish", result)
        ami.deregisterEvent('Hangup', self.on_channel_hangup)

    def err_db(self, error):
        """On database error"""
        print('error db insert')
        print(error)

    def on_failure(self, reason):
        """Unable to log in!"""
        print(reason.getTraceback())


def call(phone_number, ext):
    global extension, phone
    extension = ext
    phone = phone_number
    #manager.log.setLevel(logging.DEBUG)
    #logging.basicConfig()
    c = OnCall()
    reactor.callWhenRunning(c.main)
