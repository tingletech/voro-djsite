import threading
import sys
import socket
from django.test import TestCase
from django.core.handlers.wsgi import WSGIHandler
from django.core.servers import basehttp
from django.db import connection
from django.core.management import call_command 

class TestCaseLiveServer(TestCase):
    def start_test_server(self, address='localhost', port=8000):
        """Creates a live test server object (instance of WSGIServer)."""
        self.server_thread = TestServerThread(address, port)
        if hasattr(self, 'fixtures'):
            self.server_thread.fixtures = self.fixtures
        self.server_thread.start()
        self.server_thread.started.wait()
        if self.server_thread.error:
            raise self.server_thread.error

    def stop_test_server(self):
        if self.server_thread:
            self.server_thread.join()


class TestServerThread(threading.Thread):
    """Thread for running a http server while tests are running."""

    def __init__(self, address, port):
        self.address = address
        self.port = port
        self._stopevent = threading.Event()
        self.started = threading.Event()
        self.error = None
        super(TestServerThread, self).__init__()

    def run(self):
        """Sets up test server and database and loops over handling http requests."""
        try:
            handler = basehttp.AdminMediaHandler(WSGIHandler())
            server_address = (self.address, self.port)
            httpd = StoppableWSGIServer(server_address, basehttp.WSGIRequestHandler)
            httpd.set_app(handler)
            #self.started.set()
        except basehttp.WSGIServerException, e:
            self.error = e
            self.started.set()
            return

        # Must do database stuff in this new thread if database in memory.
        from django.conf import settings
        print "TEST_DATABASE_NAME:", settings.TEST_DATABASE_NAME
        if (settings.DATABASE_ENGINE == 'sqlite3' or settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3') \
            and (not settings.TEST_DATABASE_NAME or settings.TEST_DATABASE_NAME == ':memory:'):
            print "CREATE TEST DB IN MEMORY"
            sys.stdout.flush()
            db_name = connection.creation.create_test_db()
            # Import the fixture data into the test database.
            if hasattr(self, 'fixtures'):
                # We have to use this slightly awkward syntax due to the fact
                # that we're using *args and **kwargs together.
                print "LOADING TEST FIXTURE DATA"
                call_command('loaddata', *self.fixtures, **{'verbosity': 0})
                print "LOADED TEST FIXTURES", self.fixtures
                sys.stdout.flush()

        self.started.set()
        # Loop until we get a stop event.
        while not self._stopevent.isSet():
            httpd.handle_request()

        if (settings.DATABASE_ENGINE == 'sqlite3' or settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3') \
            and (not settings.TEST_DATABASE_NAME or settings.TEST_DATABASE_NAME == ':memory:'):
            connection.creation.destroy_test_db(db_name)
        httpd.socket.close() #NOTE: THIS IS CRUCIAL

    def join(self, timeout=None):
        """Stop the thread and wait for it to finish."""
        self._stopevent.set()
        threading.Thread.join(self, timeout)

class StoppableWSGIServer(basehttp.WSGIServer):
    """WSGIServer with short timeout, so that server thread can stop this server."""

    def server_bind(self):
        """Sets timeout to 1 second."""
        basehttp.WSGIServer.server_bind(self)
        self.socket.settimeout(1)

    def get_request(self):
        """Checks for timeout when getting request."""
        try:
            sock, address = self.socket.accept()
            sock.settimeout(None)
            return (sock, address)
        except socket.timeout:
            raise
