#!/usr/bin/python

import sys
import logging
from asterisk.agi import *

logging.basicConfig(filename='easy.log',level=logging.DEBUG)
logging.info('Before calling AGI')
agi = AGI()
agi.answer()
logging.info('After calling AGI')
agi.verbose("python agi started")
callerId = agi.env['agi_callerid']
agi.verbose("call from %s" % callerId)
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
