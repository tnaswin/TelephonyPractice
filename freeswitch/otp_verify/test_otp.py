from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor

import cgi

class FormPage(Resource):
    def render_GET(self, request):
        return '''
                <html><body>
                <form method="POST">
                Enter your mobile nunber: <input name="mobile" type="text" />
                <button type="submit" value="Submit">Request OTP</button>
                </form>
                </body></html>'''

    def render_POST(self, request):
        self.ext = (cgi.escape(request.args["mobile"][0]),)
        return '<html><body>You submitted: %s</body></html>' % (cgi.escape(request.args["mobile"][0]),)


root = Resource()
root.putChild("form", FormPage())
factory = Site(root)
reactor.listenTCP(8880, factory)
reactor.run()
