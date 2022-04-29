"""Static methods to format / handle json objects in program

Written : 23/04
Author  : Matthew Holsey
"""

import json


def format_json_response(response, success, add_change=False, errors=None, add_deposit_val=False,
                         add_v_machine_coins=False):
    """
    Function to format parameters into a json object

    :param add_deposit_val: int         : Add current depo amount to return value
    :param response: String             : String contianing action state
    :param success: Boolean             : True if success else False
    :param add_change: Dict             : Dict containing change left from purchase
    :param add_v_machine_coins: Boolean : Add Dict containing coins in machine
    :param errors: str/list/dict        : Variable containing any errors

    :return: bytes
    """
    response_dict = {"response": response,
                     "success": success}

    if add_change:
        if isinstance(add_change, dict):
            # Adds a dict of the coins
            response_dict["coins"] = add_change

    if add_deposit_val:
        response_dict["deposit_total"] = add_deposit_val

    if add_v_machine_coins:
        if isinstance(add_v_machine_coins, dict):
            response_dict["machine_coins"] = add_v_machine_coins

    if errors:
        errors_dict = {}
        if isinstance(errors, list):
            for index, item in enumerate(errors):
                errors_dict[index] = item
        if isinstance(errors, dict):
            errors_dict = errors
        if isinstance(errors, str):
            errors_dict[1] = errors
        response_dict["errors"] = errors_dict

    json_object = json.dumps(response_dict, indent=4)

    return str(json_object).encode()


def parse_json_in_to_dict(json_str):
    """
    return dict from the json object passed

    :param json_str : Json Obj   : Json read from program socket
    :return:        : Dict       : Dict representation of json
    """
    try:
        return json.loads(json_str)

    except Exception as e:
        raise ValueError(f"Cannot convert {json_str} to jsonObj")


