"""Example script to generate a call to connect a remote channel"""
from starpy import manager
from twisted.internet import reactor
import sys
import logging


def main(channel='sip/1001', connectTo=('phones', '1001', '1')):
    f = manager.AMIFactory('aswin', '12345678')
    df = f.login(ip='192.168.5.86')

    def onLogin(protocol):
        """On Login, attempt to originate the call"""
        context, extension, priority = connectTo
        df = protocol.originate(channel, context,
                                extension, priority,)

        def onFinished(result):
            df = protocol.logoff()

            def onLogoff(result):
                reactor.stop()
            return df.addCallbacks(onLogoff, onLogoff)

        def onFailure(reason):
            print(reason.getTraceback())
            return reason
        df.addErrback(onFailure)
        df.addCallbacks(onFinished, onFinished)
        return df

    def onFailure(reason):
        """Unable to log in!"""
        print(reason.getTraceback())
        reactor.stop()
    df.addCallbacks(onLogin, onFailure)
    return df


if __name__ == "__main__":
    manager.log.setLevel(logging.DEBUG)
    logging.basicConfig()
    reactor.callWhenRunning(main)
    reactor.run()
