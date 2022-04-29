"""Server class
Contains program API and socket setup

Assuming 1 connection / call at a time

Written : 23/04
Author  : Matthew Holsey
"""
import select
import socket
import time
import logging
import traceback

from Server.json_IO import *
from VendingMachineDir.VM_globals import Globals


class Server:
    def __init__(self):
        self.sock = None
        self.tcp_port = 22222
        self.conn = None
        self.timeout = 5

    def init_server(self):
        """
        Function to setup simple socket listener
        Bound to port 22222
        Accepts 1 connection at a time
        Runs until program is exited - Future : Accept api call for close.
        """

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind(('127.0.0.1', self.tcp_port))
            # only allow 1 connection at a time..
            # Assuming only 1 person using it at a time
            self.sock.listen(1)
            while Globals.running:
                # Wait for the next connection
                try:
                    self.conn, addr = self.sock.accept()
                except OSError as err:
                    # Check if the error came from a 'closed' conn
                    if "closed" in str(self.conn):
                        # If no msg, close connection
                        self.conn.close()
                        continue
                    raise err
                except Exception as e:
                    raise e

                self.handle_connection()
        except Exception as e:
            print(traceback.format_exc())
            print(e)
        finally:
            self.sock.close()

    def close_connection(self):
        self.conn.close()

    def handle_connection(self):
        """
        Function to read from the socket and pass the data read to be parsed

        Closes connection on function finish
        """
        data = ""
        try:
            data = self.read_data()
            response = self.handle_response(parse_json_in_to_dict(data))
            # response is json object at the moment, need to convert to bytes in order to send
            self.conn.sendall(response)

        except ValueError:
            logging.warning(f"Couldn't parse json from string: '{data}'")
            self.conn.sendall(format_json_response("Fail", success=False,
                                                   errors="Value error: Couldn't parse data read into json obj"))
        except TimeoutError:
            logging.warning("Timeout during socket read - server")
            self.conn.sendall(format_json_response("Fail", success=False,
                                                   errors="Timeout during read"))
        except Exception as e:
            logging.error(f"Unknown exception hit during parse of data: {e}")
            Globals.running = False
        finally:
            # Closing connection / socket on finish
            self.close_connection()

    def read_data(self):
        ready = self.check_read_pipe()
        if ready[0]:
            data = self.conn.recv(4096)
            data = data.decode("utf-8")
            start_time = time.time()
            # Loop until full json object
            while not data.count('{') == data.count('}') or not data:
                data += self.conn.recv(4096).decode("utf-8")
                if time.time() - start_time > self.timeout:
                    raise TimeoutError

            return data

        raise TimeoutError

    def check_read_pipe(self):
        ready = select.select([self.conn], [], [], self.timeout)
        return ready

    def handle_response(self, json_dict):
        # Keep in this order - Handle deposit before purchase
        if "deposit" in json_dict:
            # Can only do purchase after making deposit
            if "purchase" in json_dict:
                return self.handle_purchase(json_dict)
            return self.handle_deposit(json_dict)
        if "purchase" in json_dict:
            return format_json_response("Fail", success=False, errors="Cannot make purchase without a deposit!")

    def handle_purchase(self, json_dict):
        """
        Function to handle api 'purchase' of item

        :param: json_dict   : Dict  : dictionary containing json read from socket

        :return: function call  : JSON  : Json object contianing api response
        """

        # Handle deposit first
        json_depo_str = self.handle_deposit(json_dict)
        json_depo_obj = json.loads(json_depo_str)          # There's more efficient ways than converting to str and back
        # Check 'success' value is there and that it was true
        if "success" not in json_depo_obj or not json_depo_obj["success"]:
            return json_depo_str

        # checking necessary key in json
        if "value" not in json_dict["purchase"]:
            logging.debug("Fail: 'Value' key not found in json")
            return format_json_response("Fail", success=False, errors="'Value' key not found in json.")

        value = json_dict["purchase"]["value"]
        change = Globals.v_machine.user_deposited_total - value

        if change < 0:
            logging.debug("Value of product being bought was greater than total change left in machine")
            return format_json_response("Fail", success=False,
                                        errors="Not enough money deposited into system from user!")

        if int(change) > Globals.v_machine.calc_current_change_total():
            logging.debug("Value of product being bought was greater than total change left in machine")
            return format_json_response("Fail", success=False, errors="Not enough change in machine left for purchase")

        # dict of change
        return_change = Globals.v_machine.subtract_value(change)

        # Successful purchase, reduce deposit total back to 0
        Globals.v_machine.user_deposited_total = 0

        return format_json_response(f"Successful purchase.", success=True, add_change=return_change)

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
        for key, value in json_dict["deposit"]["coins"].items():
            if int(key) not in Globals.v_machine.coin_names:
                if not errors:
                    errors = []
                errors.append("Invalid key found in json : '{key}'. Skipping value.")
                logging.warning(f"Invalid key found in json : '{key}'. Skipping value.")
            else:
                # Add the quantity passed to the current coins in vending machine
                Globals.v_machine.current_coins[int(key)] += int(value)
                # Increase current deposit amount
                Globals.v_machine.user_deposited_total += int(key) * int(value)

        return format_json_response("Successful deposit.", success=True, errors=errors,
                                    add_deposit_val=Globals.v_machine.user_deposited_total)


