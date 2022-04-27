"""Server class
Contains program API and socket setup

Assuming 1 connection / call at a time

Written : 23/04
Author  : Matthew Holsey
"""


import socket
import time
import logging

from Server.json_IO import *
from VendingMachineDir.VM_globals import Globals


class Server:
    def __init__(self):
        self.sock = None
        self.tcp_port = 22222
        self.conn = None

    def init_server(self):
        """
        Function to setup simple socket listener
        Bound to port 22222
        Accepts 1 connection at a time
        Runs until program is exited - Future : Accept api call for close.
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', self.tcp_port))
        # only allow 1 connection at a time..
        # Assuming only 1 person using it at a time
        self.sock.listen(1)

        while Globals.running:
            # Wait for the next connection
            self.conn, addr = self.sock.accept()

            self.handle_connection()

    def handle_connection(self):
        """
        Function to read from the socket and pass the data read to be parsed

        Closes connection on function finish
        """
        data = self.conn.recv(4096)
        data = str(data)
        start_time = time.perf_counter()
        # Loop until full json object
        while not data.count('{') == data.count('}'):
            data += str(self.conn.recv(4096))
            if start_time - time.perf_counter() > 5:
                logging.warning("Timeout during read")
                break
            # Note - May be more efficient to join list of strings
            # But, input JSON str is too small to make 'big' impact on efficiency
        try:
            response = self.handle_response(parse_json_in_to_dict(data))

            # response is json object at the moment, need to convert to bytes in order to send
            self.conn.sendall(response)
        except Exception as e:
            logging.error(f"Exception hit during parse of data: {e}")
        finally:
            # Close the connection on finish
            self.conn.close()
            self.conn = None

    def handle_response(self, json_dict):
        # Keep in this order - Handle deposit before purchase
        if "deposit" in json_dict:
            return self.handle_deposit(json_dict)
        if "purchase" in json_dict:
            return self.handle_purchase(json_dict)

    def handle_purchase(self, json_dict):
        """
        Function to handle api 'purchase' of item

        :param: json_dict   : Dict  : dictionary containing json read from socket

        :return: function call  : JSON  : Json object contianing api response
        """

        # checking necessary key in json
        if "value" not in json_dict["purchase"]:
            logging.debug("Fail: 'Value' key not found in json")
            return format_json_response("Fail", success=False, errors="'Value' key not found in json.")

        value = json_dict["purchase"]["value"]

        if value > Globals.v_machine.calc_current_change_total():
            logging.debug("Value of product being bought was greater than total change left in machine")
            return format_json_response("Fail", success=False, errors="Not enough change in machine left for purchase")

        change = Globals.v_machine.subtract_value(value)

        return format_json_response(f"Successful purchase.", success=True, add_coins=change)

    def handle_deposit(self, json_dict):
        """
        Function to handle API 'deposit' of coins

        :param: json_dict       : Dict  : dictionary containing json read from socket

        :return: function call  : JSON  : Json object contianing api response
        """

        # checking necessary key in json
        if "coins" not in json_dict["deposit"]:
            logging.debug("Failed: 'coins' key not found in json")
            return format_json_response("Fail", success=False, errors="No 'coins' found in json")

        errors = None
        for key, value in json_dict["deposit"]["coins"]:
            if int(key) not in Globals.v_machine.coin_names:
                if not errors:
                    errors = []
                errors.append("Invalid key found in json : '{key}'. Skipping value.")
                logging.warning(f"Invalid key found in json : '{key}'. Skipping value.")
            else:
                # Add the quantity passed to the current coins in vending machine
                Globals.v_machine.current_coins[key] += int(value)

        return format_json_response("Successful deposit.", success=True, errors=errors,
                                    add_coins=Globals.v_machine.return_current_quantities())


