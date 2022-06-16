from application.placed_function import PlacedFunction
from enum import Enum

# types of placements


class PlacementType(str, Enum):
    PADDED_PLACEMENT = "paddedPlacement"
    UNPADDED_PLACEMENT = "unPaddedPlacement"
    PADDED_REPLACEMENT = "paddedReplacement"
    UNPADDED_REPLACEMENT = "unPaddedReplacement"


def get_placement_query(
    placement_type: PlacementType,
    max_placement_time: int,
    orchestration_id: str,
    generator_id: str = None,
    starting_function: str = None,
    starting_nodes: list[str] = None,
) -> (str | None):
    """Get the query to execute based on the placement type"""

    match placement_type:
        case PlacementType.PADDED_PLACEMENT | PlacementType.UNPADDED_PLACEMENT:
            query_command = ""
            if placement_type == PlacementType.PADDED_PLACEMENT:
                query_command = "secfaas2fogOpt"
            else:
                query_command = "secfaas2fogOptNoPad"

            # generator id cannot be None
            if generator_id is None:
                return None

            return f"{query_command}({max_placement_time}, {generator_id}, {orchestration_id}, Placement)."

        case PlacementType.PADDED_REPLACEMENT | PlacementType.UNPADDED_REPLACEMENT:
            query_command = ""
            if placement_type == PlacementType.PADDED_REPLACEMENT:
                query_command = "replacement"
            else:
                query_command = "replacementNoPad"

            # starting function cannot be None
            if starting_function is None:
                return None
            # list of starting nodes cannot be None or empty
            if starting_nodes is None or len(starting_nodes) == 0:
                return None

            to_return = f"{query_command}({max_placement_time}, {starting_function}, ["
            for node in starting_nodes:
                to_return += f"{node},"
            to_return = to_return.removesuffix(",")
            to_return += f"], {orchestration_id}, Placement)."

            return to_return

        case _:
            return None


# function used to parse prolog placement


def rec_parse_placement(dictionary: dict, placement: dict, is_guard: bool = False):
    expression = dictionary["functor"]

    match expression:
        case "fp":
            function_id: str = dictionary.get("args")[0]
            node_id: str = dictionary.get("args")[5]
            sw_reqs = dictionary.get("args")[2]

            # hardware reqs are already padded
            hw_reqs = dictionary.get("args")[3]
            memory_req = hw_reqs.get("args")[0]
            v_cpu_req = hw_reqs.get("args")[1].get("args")[0]
            mhz_req = hw_reqs.get("args")[1].get("args")[1]

            function = PlacedFunction(
                function_id, node_id, sw_reqs, memory_req, v_cpu_req, mhz_req, is_guard
            )

            return {function_id: function}
        case "if":
            guard = rec_parse_placement(dictionary.get("args")[0], placement, True)
            c1 = rec_parse_placement(dictionary.get("args")[1], placement)
            c2 = rec_parse_placement(dictionary.get("args")[2], placement)

            placement.update(guard)
            placement.update(c1)
            placement.update(c2)

            return placement
        case "par":
            c1 = rec_parse_placement(dictionary.get("args")[0][0], placement)
            c2 = rec_parse_placement(dictionary.get("args")[0][1], placement)

            placement.update(c1)
            placement.update(c2)

            return placement
        case "seq":
            c1 = rec_parse_placement(dictionary.get("args")[0], placement)
            c2 = rec_parse_placement(dictionary.get("args")[1], placement)

            placement.update(c1)
            placement.update(c2)

            return placement
        case _:
            return placement


def parse_placement(prolog_placement: dict) -> dict[str, PlacedFunction]:

    return rec_parse_placement(prolog_placement["Placement"], {})


# functions used to retrieve application chain


def rec_build_app_chain(dictionary: dict, dependencies: dict, caller):
    expression = dictionary["functor"]

    if expression == "fp":
        function: str = dictionary.get("args")[0]

        return function, function, expression
    elif expression == "if":
        guard = dictionary.get("args")[0].get("args")[0]
        c11, c12, exp_type1 = rec_build_app_chain(
            dictionary.get("args")[1], dependencies, guard
        )
        c21, c22, exp_type2 = rec_build_app_chain(
            dictionary.get("args")[2], dependencies, guard
        )

        dependencies[guard] = caller
        dependencies[c11] = guard
        dependencies[c21] = guard
        return c12, c22, expression

    elif expression == "par":
        c11, c12, exp_type1 = rec_build_app_chain(
            dictionary.get("args")[0][0], dependencies, caller
        )
        c21, c22, exp_type2 = rec_build_app_chain(
            dictionary.get("args")[0][1], dependencies, caller
        )

        return1 = (c11, c12) if exp_type1 not in ["fp", "seq"] else c12
        return2 = (c21, c22) if exp_type2 not in ["fp", "seq"] else c22

        return return1, return2, expression

    elif expression == "seq":
        c11, c12, exp_type1 = rec_build_app_chain(
            dictionary.get("args")[0], dependencies, caller
        )
        c21, c22, exp_type2 = rec_build_app_chain(
            dictionary.get("args")[1], dependencies, c12
        )

        if c21 not in dependencies and not isinstance(c21, tuple):
            if exp_type1 == "seq":
                dependencies[c21] = c12
            else:
                dependencies[c21] = (c11, c12) if c11 != c12 else c11
        if c22 not in dependencies and not isinstance(c22, tuple):
            if exp_type1 == "seq":
                dependencies[c22] = c12
            else:
                dependencies[c22] = (c11, c12) if c11 != c12 else c11
        if c11 not in dependencies and not isinstance(c11, tuple):
            dependencies[c11] = caller
        if c12 not in dependencies and not isinstance(c12, tuple):
            dependencies[c12] = caller

        return1 = (c11, c12) if exp_type1 != "fp" else c12
        return2 = (c21, c22) if exp_type2 != "fp" else c22

        return return1, return2, expression


def unpack_nested_tuples(t: tuple):
    elements = list(t)
    to_return = []
    for elem in elements:
        if isinstance(elem, tuple):
            result = unpack_nested_tuples(elem)
            to_return += result
        else:
            to_return.append(elem)

    return to_return


def build_app_chain(prolog_placement: dict) -> dict[str, str]:

    dependencies = {}

    # when we place/replace only one function of an application
    # the raw placement has a ambiguous form
    # so we build dependencies ourselves
    if prolog_placement["Placement"]["functor"] == "fp":
        function_name = prolog_placement["Placement"]["args"][0]
        dependencies[function_name] = []

        return dependencies

    _ = rec_build_app_chain(prolog_placement["Placement"], dependencies, None)

    to_return = {}

    keys = dependencies.keys()
    for key in keys:
        if not isinstance(key, tuple):
            value = dependencies.get(key)
            if isinstance(value, tuple):
                new_value = unpack_nested_tuples(value)
                to_return[key] = new_value
            else:
                # starting functions depends from None, delete it
                if value is None:
                    new_value = []
                else:
                    new_value = [value]
                to_return[key] = new_value

    return to_return
