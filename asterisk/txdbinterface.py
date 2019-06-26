from twisted.internet import threads
from twisted.internet.defer import Deferred
import logging


log = logging.getLogger("txDB")

ranconnect = 0
dbpool = None
dbtype = "mysql"
dbname = "asterisk"
username = "root"
password = "root"
host = "127.0.0.1"

if dbtype == "mysql":
    from twisted.enterprise import adbapi
    import MySQLdb
    import MySQLdb.cursors
    dbtype = 'mysql'


    class ReconnectingConnectionPool(adbapi.ConnectionPool):
        def _runInteraction(self, interaction, *args, **kw):
            try:
                return adbapi.ConnectionPool._runInteraction(self, interaction, *args, **kw)
            except MySQLdb.OperationalError, e:
                error_messages = ("mysql server has gone away", "lost connection to mysql server during query")
                if any([x in str(e).lower() for x in error_messages]):
                    log.info(" >>> Resetting DB pool...")
                    for conn in self.connections.values():
                        self._close(conn)
                    self.connections.clear()
                    return adbapi.ConnectionPool._runInteraction(self, interaction, *args, **kw)
                else:
                    raise


class txDBPool:
    def __init__(self, dbname=None, username=None, password = None,  host = None):
        global ranconnect
        if not ranconnect:
            log.debug("Running connect")
            self.connect(dbname, username, password, host)
        else:
            log.debug("Connect already ran")

    def connect(self, dbname, username, password, host):
        global ranconnect, dbpool
        ranconnect = 1
        if dbtype == 'mysql':
            dbpool = self.dbpool = ReconnectingConnectionPool('MySQLdb', db=dbname, user=username, passwd=password, host=host, cp_min=10, cp_reconnect=1, cursorclass=MySQLdb.cursors.DictCursor)
        if dbtype == 'postgres':
            dbpool = self.dbpool = adbapi.ConnectionPool(None,database=dbname, user=username, password=password, host=host, min=10 )
            df = dbpool.start()
        #df = threads.deferToThread(self.dbpool.connect)
            df.addCallbacks(self.onDBConnect, self.onDBFail)
        #dbpool.start()

    def onDBConnect(self, arg):
        log.debug("Connected to postgres DB")

    def onDBFail(self, error):
        global ranconnect
        ranconnect =0
        log.error("Failed to connect to postgres DB")

class txDBInterface:
    def __init__(self, *query):
        self.dbpool = dbpool
        self.resultdf = Deferred()
        self.query = query
        self.tries = 0

    def runQuery(self):
        log.debug("Running query - %s"%str(self.query))
        self.tries +=1
        try:
            df = self.dbpool.runQuery(*self.query)
            df.addCallbacks(self.onResult, self.onFail)
        except adbapi.ConnectionLost:
            log.error("We lost connection to db re-running the query")
            return self.runQuery()
        return self.resultdf

    def onResult(self, result):
        self.resultdf.callback(result)

    def onFail(self, error):
        if isinstance(error, adbapi.ConnectionLost):
            log.info("We lost connection to db. re-running the query")
            if self.tries < 3:
                return self.runQuery()
        self.resultdf.errback(error)


def execute(*query):
    txdbi = txDBInterface(*query)
    return txdbi.runQuery()


txDBPool(dbname, username, password, host)
