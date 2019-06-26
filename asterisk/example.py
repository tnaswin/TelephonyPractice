from asterisk.agi import *

agi = AGI()

agi.verbose("python agi started")

# Get variable environment
extension = agi.env['agi_extension']

# Get variable in dialplan
phone_exten = agi.get_variable('PHONE_EXTEN')

# Set variable, it will be available in dialplan
agi.set_variable('EXT_CALLERID', '1')
