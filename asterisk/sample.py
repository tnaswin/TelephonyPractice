   #!/usr/bin/python
   import sys
   env = ""
   while(env != "\n")
       env = sys.stdin.readline()
   sys.stdout.write('SAY NUMBER 123 "*#"\n')
   sys.stdout.flush()
   res = sys.stdin.readline()
   sys.stderr.write("Received %s\n"%res)
   sys.stderr.flush()
