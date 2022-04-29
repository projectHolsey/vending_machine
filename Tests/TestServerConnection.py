import unittest
import socket
import time
import select
import threading
import traceback
from unittest.mock import Mock

from Server.server_handler import Server
from VendingMachineDir.VM_globals import Globals


class TestServerConnection(unittest.TestCase):

    def setUp(self):
        # Create new server on every test
        self.Server = Server()
        self.Server.timeout = 0.5       # NOTE - Setting small timeout to speed up connection tests
        Globals.running = True
        self.server_thread = threading.Thread(target=self.Server.init_server)
        self.server_thread.start()
        time.sleep(1)

    def tearDown(self):
        # Stop and destroy server
        try:
            Globals.running = False
            time.sleep(1)
            if self.Server.sock:
                self.Server.sock.close()
            self.server_thread.join()
            # allowing sockets to close
            time.sleep(1)
        except Exception as e:
            print(e)

    def test_simple_connection(self):
        """
        Testing simple connect
        -- Expecting 'timeout' error displayed from server as no data is sent
        :return:
        """
        s = socket.socket()
        try:
            s.connect(('127.0.0.1', 22222))
        except Exception as e:
            self.fail(f"Exception on simple connect : {e}")
        finally:
            s.close()

    def test_server_accepts_async_connections(self):
        """
        Checking async connections are valid

        Expecting 2 timeouts as there's no data sent across socket to server
        Expecting both connection attempts to connect without error
        """
        s = socket.socket()
        try:
            s.connect(('127.0.0.1', 22222))
        except Exception as e:
            self.fail(f"Exception on simple connect : {e}")
        finally:
            s.close()

        time.sleep(2)

        s2 = socket.socket()
        try:
            s2.connect(('127.0.0.1', 22222))
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Second connection failed unexpectedly :  {e}")
        finally:
            s2.close()

    def test_simple_check_timeout(self):
        """
        Forcing timeout error from server
        Expected server to response with timeout error
        """
        s = socket.socket()
        try:
            s.connect(('127.0.0.1', 22222))
            time.sleep(3)
            self.assertTrue("timeout" in s.recv(4096).decode("UTF-8").lower())

        except Exception as e:
            self.fail(f"Exception in timeout test : {e}")
        finally:
            s.close()

    def test_none_json_obj_send(self):
        """
        Forcing json parse error by sending invalid json string
        Expecting value error to be returned from server
        """
        s = socket.socket()
        try:
            s.connect(('127.0.0.1', 22222))
            s.send(b"None json formatted string")
            self.assertTrue("value error" in s.recv(4096).decode("UTF-8").lower())

        except Exception as e:
            self.fail(f"Exception in value error test : {e}")
        finally:
            s.close()