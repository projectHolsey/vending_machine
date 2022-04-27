"""Class to handle program arguments passed on command line

Written : 23/04
Author  : Matthew Holsey
"""


import re
import os

from VendingMachineDir.VM_globals import Globals


class ArgHandler:
    def __init__(self):
        self.error_flag = False
        # self.return_xml = False       # Future - Add response in XML format

    def parse_args(self, arguments):
        if arguments.state_file:
            self.handle_state_file(arguments)

    def handle_state_file(self, arguments):
        """
        Function to add new vending machine 'state' on startup.
        Checking for file existence, reading and checking format

        If successful, the global vending machine variable will
        contain a new default state for this instance of the program.

        :param arguments: ArgParse arguments passed to program
        """
        if os.path.isfile(arguments.state_file):
            # Use context so we don't leave file open
            with open(arguments.state_file, 'r') as infile:
                for line in infile:

                    # removing trailing chars / Whitespace
                    line = str(line).strip()

                    # Use handle deposit for each line
                    if not self.check_csv_line(line):
                        continue

                    # CSV line in form 'Coin:Quantity'
                    coin_value = line.split(",")
                    if int(coin_value[0]) in Globals.v_machine.default_state:
                        # As we're setting the new state, this is overridden, not appended to
                        Globals.v_machine.default_state[int(coin_value[0])] = int(coin_value[1])
                    else:
                        print(f"Coin '{coin_value[0]}', does not exist!")

            # Copy the new default state of coins in machine into current coins
            Globals.v_machine.current_coins = Globals.v_machine.default_state.copy()
            Globals.v_machine.current_change_total = Globals.v_machine.calc_current_change_total()

        else:
            print(f"Could not find file, is path correct? {arguments.state_file}")

    def check_csv_line(self, line):
        """
        Check the line read from CSV file is formatted correctly
        Prints any errors to terminal

        :param line:    Str     : String line read from csv file
        :return:        Boolean : True if correctly formatted else False
        """
        if not re.match("\d+,\d+", line):
            print("Invalid line in csv, required form 'int,int'")
            return False

        coin_quantity = line.split(",")
        for item in coin_quantity:
            try:
                x = int(item)
            except ValueError:
                print(f"value : '{item}' is invalid. Requires whole numbers")
                return False

        return True
