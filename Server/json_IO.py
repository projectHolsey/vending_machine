"""Static methods to format / handle json objects in program

Written : 23/04
Author  : Matthew Holsey
"""

import json


def format_json_response(response, success, add_coins=False, errors=None):
    """
    Function to format parameters into a json object

    :param response: String         : String contianing action state
    :param success: Boolean         : True if success else False
    :param add_coins: Dict          : Dict containing coins returned
    :param errors: str/list/dict    : Variable containing any errors

    :return: Json object
    """
    response_dict = {"response": response,
                     "success": success}

    if add_coins:
        if isinstance(add_coins, dict):
            # Adds a dict of the coins
            response_dict["coins"] = add_coins

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

    return json_object


def parse_json_in_to_dict(json_str):
    """
    return dict from the json object passed

    :param json_str : Json Obj   : Json read from program socket
    :return:        : Dict       : Dict representation of json
    """
    return json.load(json_str)



