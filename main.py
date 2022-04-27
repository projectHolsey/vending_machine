"""Main entry point for python program

Written : 23/04
Author  : Matthew Holsey
"""


from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

from VendingMachineDir.VendingMachine import VendingMachine
from VendingMachineDir.VM_globals import Globals
from Server.server_handler import Server
from ArgHandler import ArgHandler


def program_init():
    """
    Function to initiate global / program variables
    """
    # Create a VEnding machine instance - global
    Globals.v_machine = VendingMachine()
    # Create a Server handler - Global
    Globals.server = Server()
    # Set the running glad to true
    Globals.running = True


if __name__ == '__main__':
    """entry point"""
    parser = ArgumentParser(prog='PROG', formatter_class=RawDescriptionHelpFormatter)

    parser.add_argument("-sf", "--state_file",
                        help="Set state as csv formatted file", metavar="<FILE>")

    # parser.add_argument("-dr", "--display_response",
    #                     help="Display list of possible responses")

    args = parser.parse_args()

    # Setup program objects
    program_init()

    # Handle program arguments
    x = ArgHandler()
    x.parse_args(args)

    # start listening for messages
    Globals.server.init_server()




