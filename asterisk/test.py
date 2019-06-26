#!/usr/bin/python

import sys
from asterisk.agi import *

agi = AGI()
agi.verbose("Before Answering")
ch1 = agi.channel_status()
agi.verbose("Channel : %s" % ch1)
agi.answer()
agi.verbose("Call answered, Python AGI Started")
ch2 = agi.channel_status()
agi.verbose("Channel : %s" % ch2)
callerId = agi.env['agi_callerid']
agi.verbose("Call from %s" % callerId)
while True:
    agi.stream_file('hello-world')
    result = agi.wait_for_digit(-1)
    agi.verbose("got digit %s" % result)
    if result.isdigit():
        agi.say_number(result)
    else:
        agi.verbose("bye!")
        agi.hangup()
        sys.exit()
