""" Class for controlling vending machine state

If no arguments passed, assume 'default state' on startup

Written : 23/04
Author  : Matthew Holsey
"""
import math


class VendingMachine:

    def __init__(self, state=None):
        """

        :param state:   Dict[ str, str ]     : Containing dictionary of coins and quantity
        """

        # Default state - Each (GBP) coin issued quantity of 5
        self.default_state = {1: 5, 2: 5, 5: 5, 10: 5, 20: 5, 50: 5, 100: 5, 200: 5}
        if state:
            self.default_state = state

        # Assign current coins to default at startup
        self.current_coins = self.default_state.copy()
        self.current_change_total = self.calc_current_change_total()

        # Storing total user deposit for purchase ( e.g. multiple deposits )
        self.user_deposited_total = 0

        # List of coin_names
        self.coin_names = [1, 2, 5, 10, 20, 50, 100, 200]
        self.coin_names.sort()

    def calc_current_change_total(self):
        """
        Returning value of all of the coins left in the vending machine

        :return: int    : Value of all
        """
        ret_value = 0
        for key in self.current_coins:
            ret_value += int(self.current_coins[key]) * int(key)
        return ret_value

    # Return current quantity of coins held
    def return_current_quantities(self):
        return self.current_coins

    # Set new quantity of coins held
    def set_quantities(self, state):
        self.current_coins = state

    def add_coins(self, user_deposited):
        """
        Add coins from user to change in vending machine

        :param user_deposited: Dict{int, int}   : Dictionary of coins deposited
        :return: N/A
        """
        for key, val in user_deposited:
            self.current_coins[key] += val

    def reset_coins_to_default(self):
        self.current_coins = self.default_state.copy()

    # remove coins from quantity
    def subtract_value(self, product_value):
        """
        Return correct change

        :param product_value: int                :   Value of product bought (in pence)
        :return: ret_change : dict {int, int}    :   Coin names and values used
        """

        ret_change = {}
        # Making sure biggest value coins are used first.
        self.coin_names.sort(reverse=True)
        for item in self.coin_names:

            if (int(self.current_coins[item]) > 0) and (int(product_value) / int(self.current_coins[item]) > 0):

                coin_quantity = math.floor(int(product_value) / int(item))

                # if there's not enough of this coin to take from, use as many as available
                if 0 < int(self.current_coins[item]) < coin_quantity:
                    coin_quantity = int(self.current_coins[item])
                    self.current_coins[item] = 0
                else:
                    # Minus a coin from vending machine's coin stack
                    self.current_coins[item] -= coin_quantity

                if coin_quantity > 0:
                    # Add item to change
                    ret_change[item] = coin_quantity

                # Subtract coin value from remaining product value
                product_value -= (int(item) * coin_quantity)

        return ret_change
