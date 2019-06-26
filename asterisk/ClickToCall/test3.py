#! /usr/bin/python

import sys
import cgi
import logging

import clicktocall

from twisted.internet import reactor
from twisted.web.server import Site, NOT_DONE_YET
from twisted.web.resource import Resource

from starpy import manager

log = logging.getLogger("Test")
ext = 0


class FormPage(Resource):
    "Form 1"

    def render_GET(self, request):
        return '''
               <html><body>
               <form method="POST">
               Enter mobile number:
               <input name="mobile" type="text">
               <button type="submit" value="submit">
               Click to Call</button></form>
               </body></html>
               '''

    def render_POST(self, request):
        global ext
        ext = cgi.escape(request.args["mobile"][0])
        reactor.callLater(1, self._delayed_render, request)
        print "Extension : ", ext
        clicktocall.call(ext)
        return NOT_DONE_YET

    def _delayed_render(self, request):
            request.write(
                '''
                <html><body>
                Calling Extension : %s
                <form action="/form2" method="POST">
                <button type="submit" value="Submit">Call Details</button>
                </form></body></html>
                ''' % ext
                )


class NewPage(Resource):
    """Form 2."""

    def render_POST(self, request):
        reactor.callLater(1, self.delayed_render2, request)
        return NOT_DONE_YET

    def delayed_render2(self, request):
        request.write('''
                      <html><body><br>Call Details : <br></body></html>
                      ''' )
        call_record = clicktocall.cdr
        duration = clicktocall.end - clicktocall.start
        for k,v in call_record[1].items():
            if k == 'exten':
                print "Extension : ", v
                request.write('''
                              <html><body>
                              <br>Extension : %s <br>
                              </body></html>
                              ''' % v)
            if k == 'channel':
                print "Channel : ", v
                request.write('''
                              <html><body>
                              <br>Caller : %s
                              </body></html>
                              ''' % v)
            if k == 'uniqueid':
                print "Unique Caller ID : ", v
                request.write('''
                              <html><body>
                              <br>Caller Unique ID : %s
                              </body></html>
                              ''' % v)
        for k,v in call_record[2].items():
            if k == 'channel':
                print "Channel : ", v
                request.write('''
                              <html><body>
                              <br><br>Callee : %s
                              </body></html>
                              ''' % v)
            if k == 'uniqueid':
                print "Unique Callee ID : ", v
                request.write('''
                              <html><body>
                              <br>Callee Unique ID : %s
                               </body></html>
                              ''' % v)

        print "Start time : ", clicktocall.start
        request.write('''
                      <html><body>
                      <br><br>Start time : %s
                      </body></html>
                      ''' % clicktocall.start)
        print "End time : ", clicktocall.end
        request.write('''
                      <html><body>
                      <br>Stop time : %s
                      </body></html>
                      ''' % clicktocall.end)
        print "Duration : ", duration
        request.write('''
                      <html><body>
                      <br>Call Duration : %s
                      </body></html>
                      ''' % duration)
        request.finish()


if __name__=="__main__":
    root = Resource()
    root.putChild("form1", FormPage())
    root.putChild("form2", NewPage())
    factory = Site(root)
    reactor.listenTCP(8880, factory)
    reactor.run()
