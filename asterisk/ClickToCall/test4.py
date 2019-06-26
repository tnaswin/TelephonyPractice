#! /usr/bin/python

import sys
import cgi
import logging

import txdbinterface as txdb
import clicktocall

from twisted.internet import reactor
from twisted.web.server import Site, NOT_DONE_YET
from twisted.web.resource import Resource

from starpy import manager

log = logging.getLogger("Test")
ext = 0
requests = None


class FormPage(Resource):
    "Form 1"

    def render_GET(self, request):
        return '''
               <html><body>
               <form method="POST">
               Enter mobile number:
               <input name="mobile" type="text" required>
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
        reactor.callLater(1, self.getUserFromDb, request)
        return NOT_DONE_YET

    def getUserFromDb(self, request):
        global requests
        requests = request
        if clicktocall.uid == 0:
            requests.write('''
                          <html><body>
                          <br>CALL REJECTED <br>
                          </body></html>
                          ''')
            requests.finish()
        else:
            query = "select * from cdr where uniqueid = %s or \
                    uniqueid = %s" % (clicktocall.uid, clicktocall.uid2)
            print query
            df = txdb.execute(query)
            df.addCallback(self.onDb)
            df.addErrback(self.errDb)

    def onDb(self, result):
        print("result db")
        print result
        self.result = result[len(result)-1]
        print("Hello : ", self.result)
        requests.write('''
                      <html><body>
                      <br>CDR : %s <br>
                      </body></html>
                      ''' % self.result)
        requests.finish()

    def errDb(self, error):
        print('error db')
        print(error)


if __name__=="__main__":
    root = Resource()
    root.putChild("form1", FormPage())
    root.putChild("form2", NewPage())
    factory = Site(root)
    reactor.listenTCP(8880, factory)
    reactor.run()
