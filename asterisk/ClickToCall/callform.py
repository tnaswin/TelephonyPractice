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
    "Form 1 to get the local extension"

    def render_GET(self, request):
        return '''
               <html><body>
               <form method="POST">
               Enter mobile number:
               <input name="mobile" type="text" required><br><br>
               Enter the extension:
               <input name="ext" type="text" required><br><br>
               <button type="submit" value="submit">
               Click to Call</button></form>
               </body></html>
               '''

    def render_POST(self, request):
        global ext
        phone_number = cgi.escape(request.args["mobile"][0])
        ext = cgi.escape(request.args["ext"][0])
        reactor.callLater(1, self._delayed_render, request)
        print "Phone Number : ", phone_number
        print "Extension : ", ext
        clicktocall.call(phone_number, ext)
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
    """Form 2 to request and display CDR"""

    def render_POST(self, request):
        reactor.callLater(1, self.get_user_from_db, request)
        return NOT_DONE_YET

    def get_user_from_db(self, request):
        """Retrieves call record from database"""
        global requests
        requests = request
        """
        if clicktocall.uid1 == 0:
            requests.write('''
                          <html><body>
                          <br>CALL REJECTED <br>
                          </body></html>
                          ''')
            requests.finish()
        else:
        """
        query = "select * from cdrdb where uniqueid = '%s'" % clicktocall.uid
        print query
        df = txdb.execute(query)
        df.addCallback(self.on_db)
        df.addErrback(self.err_db)

    def on_db(self, result):
        """Fetch the db record and display"""
        print("result select db")
        print result
        if result:
            print result
            self.result = result[len(result)-1]
            print("Hello : ", self.result)
            requests.write('''
                          <html><body>
                          <br>CDR : %s <br>
                          </body></html>
                          ''' % self.result)
            requests.finish()
        else:
            print("Empty")
            requests.write('''
                          <html><body>
                          <br>No Call Details Found<br>
                          </body></html>
                          ''')
            requests.finish()

    def err_db(self, error):
        """On database error"""
        print('error db')
        print(error)


if __name__=="__main__":
    root = Resource()
    root.putChild("form1", FormPage())
    root.putChild("form2", NewPage())
    factory = Site(root)
    reactor.listenTCP(8880, factory)
    reactor.run()
