
#!/usr/bin/python
# Import module required.
import sys
# Read and ignore AGI environment (read until blank line)
env = ""
while(env != "\n"):
    env = sys.stdin.readline()
# Send Asterisk a command
sys.stdout.write('SAY NUMBER 123 "*#"\n')
# *must* flush the data or Asterisk won't get it
sys.stdout.flush()
# Read response from Asterisk
res = sys.stdin.readline()
# Show the response received on the Asterisk console
sys.stderr.write("Received %s\n"%res)
# And the obligatory flush
sys.stderr.flush()
