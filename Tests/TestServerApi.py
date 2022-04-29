import json
import select
import unittest
import time
import threading
import socket

from Server.server_handler import Server
from VendingMachineDir.VM_globals import Globals
from VendingMachineDir.VendingMachine import VendingMachine


class TestServerApi(unittest.TestCase):

    def setUp(self):
        # Create new server on every test
        self.Server = Server()
        self.Server.timeout = 0.5       # NOTE - Setting small timeout to speed up connection tests
        Globals.running = True
        self.server_thread = threading.Thread(target=self.Server.init_server)
        self.server_thread.start()
        time.sleep(1)
        Globals.v_machine = VendingMachine()

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
            # Resetting state
            Globals.v_machine = None
        except Exception as e:
            print(e)

    def _create_connection(self):
        """
        Default create connection for each test
        """
        try:
            connection = socket.socket()
            connection.connect(('127.0.0.1', 22222))
            return connection
        except Exception as e:
            self.fail(f"Problem creating connection to server! {e}")

    def test_valid_deposit(self):
        """
        Sending valid json
        Expecting "success" boolean to return true
        """
        connection = self._create_connection()

        j_input = {"deposit": {"coins": {"1": 1, "2": 1}}}
        json_formatted_input = json.dumps(j_input, indent=4)

        connection.sendall(str(json_formatted_input).encode())

        received = connection.recv(4096)
        # decode to string
        received = received.decode()
        json_obj = json.loads(received)

        if "success" in json_obj:
            self.assertTrue(json_obj["success"] is True,
                            "Expected successful action for valid deposit")
        else:
            self.fail("Did not receive 'success' boolean in json obj return")

        connection.close()

    def test_valid_deposit_total(self):
        """
        Sending valid json
        Expecting "success" boolean to return true
        Checking total deposit value is correct
        """
        connection = self._create_connection()

        j_input = {"deposit": {"coins": {"1": 1, "2": 1}}}
        json_formatted_input = json.dumps(j_input, indent=4)

        connection.sendall(str(json_formatted_input).encode())

        received = connection.recv(4096)
        # decode to string
        received = received.decode()
        json_obj = json.loads(received)

        # Would be better to format back to JSON and check json["success"] == true
        if "success" in json_obj:
            self.assertTrue(json_obj["success"] is True,
                            "Expected successful action for valid deposit")
        else:
            self.fail("Did not receive 'success' boolean in json obj return")

        self.assertTrue(json_obj["deposit_total"] == 3,
                        "Expected total deposit value of 3 for valid deposit")

        connection.close()

    def test_deposit_ignores_bad_coins(self):
        """
        Sending valid json with a none-existent coin
        Expecting "success" boolean to return true

        Expecting deposit amount to only be the valid coin value total (1)
        """
        connection = self._create_connection()

        j_input = {"deposit": {"coins": {"1": 1, "22": 1}}}
        json_formatted_input = json.dumps(j_input, indent=4)

        connection.sendall(str(json_formatted_input).encode())

        received = connection.recv(4096)
        # decode to string
        received = received.decode()

        json_obj = json.loads(received)

        if "success" in json_obj:
            self.assertTrue(json_obj["success"] is True,
                            "Expected successful action for valid deposit")
        else:
            self.fail("Did not receive 'success' boolean in json obj return")

        self.assertTrue(json_obj["deposit_total"] == 1,
                        "Expected total deposit value of 3 for valid deposit")

        connection.close()

    def test_invalid_deposit_format(self):
        """
        Checking invalid deposit format returns success = False
        """
        connection = self._create_connection()

        j_input = {"deposit": {"coin": {"1": 1, "22": 1}}}
        json_formatted_input = json.dumps(j_input, indent=4)

        connection.sendall(str(json_formatted_input).encode())

        received = connection.recv(4096)
        # decode to string
        received = received.decode()

        json_obj = json.loads(received)
        if "success" in json_obj:
            self.assertTrue(json_obj["success"] is False,
                            "Expected success to be false not true for bad input")
        else:
            self.fail("Did not receive 'success' boolean in json obj return")

        connection.close()

    """
    Handling purchases
    > Check simple
    > Check change simple
    > Check change exact
    
    > Check can't make purchase without deposit
    > Check deposit value > purchase value
    > Check double deposit is valid with purchase
    """

    def test_valid_purchase(self):
        """
        Sending a valid purchase
        Expecting boolean 'success' = True

        """
        connection = self._create_connection()

        j_input = {"deposit": {"coins": {"1": 1, "2": 1}}, "purchase": {"value": 1}}
        json_formatted_input = json.dumps(j_input, indent=4)

        connection.sendall(str(json_formatted_input).encode())

        x = select.select([], [connection], [], 5)
        if x[1]:
            received = connection.recv(4096)
            # decode to string
            received = received.decode()

            json_obj = json.loads(received)
            if "success" in json_obj:
                self.assertTrue(json_obj["success"] is True,
                                "Expected success for valid purchase")
            else:
                self.fail("Did not receive 'success' boolean in json obj return")

        else:
            self.fail("Took longer than 5 seconds for vending machine response")

        connection.close()

    def test_valid_purchase_change(self):
        """
        Sending a valid purchase
        Expecting boolean 'success' = True
        Checking change returned is valid
        """
        connection = self._create_connection()

        j_input = {"deposit": {"coins": {"1": 1, "2": 1}}, "purchase": {"value": 1}}
        json_formatted_input = json.dumps(j_input, indent=4)

        connection.sendall(str(json_formatted_input).encode())

        x = select.select([], [connection], [], 5)
        if x[1]:
            received = connection.recv(4096)
            # decode to string
            received = received.decode()

            json_obj = json.loads(received)
            if "coins" in json_obj:
                self.assertTrue(json_obj["coins"]["2"] == 1,
                                "Expected 1 x 2p change for purchase")
            else:
                self.fail("Didn't receive change from purchase!")

        else:
            self.fail("Took longer than 5 seconds for vending machine response")

        connection.close()

    def test_exact_deposit(self):
        """
        Sending a valid purchase
        Expecting boolean 'success' = True
        Checking no returned change as purchase value is same as total deposit
        """
        connection = self._create_connection()

        j_input = {"deposit": {"coins": {"1": 1, "2": 1}}, "purchase": {"value": 3}}
        json_formatted_input = json.dumps(j_input, indent=4)

        connection.sendall(str(json_formatted_input).encode())

        x = select.select([], [connection], [], 5)
        if x[1]:
            received = connection.recv(4096)
            # decode to string
            received = received.decode()

            json_obj = json.loads(received)
            if "success" in json_obj:
                self.assertTrue(json_obj["success"] is True,
                                "Expected success for valid purchase")
                self.assertTrue("coins" not in json_obj,
                                "Expected no change for exact deposit")
            else:
                self.fail("Successful purchase expected from exact change!")

        else:
            self.fail("Took longer than 5 seconds for vending machine response")

        connection.close()

    def test_purchase_without_deposit(self):
        """
        Sending 'purchase' api request without a 'deposit'
        Expecting boolean 'success' = False

        """
        connection = self._create_connection()

        j_input = {"purchase": {"value": 3}}
        json_formatted_input = json.dumps(j_input, indent=4)

        connection.sendall(str(json_formatted_input).encode())

        x = select.select([], [connection], [], 5)
        if x[1]:
            received = connection.recv(4096)
            # decode to string
            received = received.decode()

            json_obj = json.loads(received)
            if "success" in json_obj:
                self.assertTrue(json_obj["success"] is False,
                                "Expected success for valid purchase")
            else:
                self.fail("Successful purchase expected from exact change!")

        else:
            self.fail("Took longer than 5 seconds for vending machine response")

        connection.close()

    def test_too_small_deposit(self):
        """
        Sending a purchase request that is greater than amount deposited
        Expecting boolean 'success' = False

        """
        connection = self._create_connection()

        j_input = {"deposit": {"coins": {"1": 1, "2": 1}}, "purchase": {"value": 4}}
        json_formatted_input = json.dumps(j_input, indent=4)

        connection.sendall(str(json_formatted_input).encode())

        x = select.select([], [connection], [], 5)
        if x[1]:
            received = connection.recv(4096)
            # decode to string
            received = received.decode()

            json_obj = json.loads(received)
            if "success" in json_obj:
                self.assertTrue(json_obj["success"] is False,
                                "Expected success for valid purchase")
            else:
                self.fail("Successful purchase expected from exact change!")

        else:
            self.fail("Took longer than 5 seconds for vending machine response")

        connection.close()

    def test_double_deposit(self):
        """
        Make initial deposit of 3p
        Make second deposit of 3p
        Request item of value 4p
        Check change is 2p
        & valid purchase

        """
        # Make a deposit
        self.test_valid_deposit()

        connection = self._create_connection()

        j_input = {"deposit": {"coins": {"1": 1, "2": 1}}, "purchase": {"value": 4}}
        json_formatted_input = json.dumps(j_input, indent=4)

        connection.sendall(str(json_formatted_input).encode())

        x = select.select([], [connection], [], 5)
        if x[1]:
            received = connection.recv(4096)
            # decode to string
            received = received.decode()

            json_obj = json.loads(received)
            if "coins" in json_obj:
                self.assertTrue(json_obj["coins"]["2"] == 1,
                                "Expected 1 x 2p change for purchase")
            else:
                self.fail("Didn't receive change from purchase!")

        else:
            self.fail("Took longer than 5 seconds for vending machine response")

        connection.close()