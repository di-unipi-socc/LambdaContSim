from application.function import PlacedFunction

# function used to parse prolog placement

def rec_parse_placement(dictionary : dict, placement : dict, is_guard : bool):
    expression = dictionary['functor']
    if expression == 'fp':
        function_id = dictionary.get('args')[0]
        node_id = dictionary.get('args')[5]
        sw_reqs = dictionary.get('args')[2]
        
        # hardware reqs are already padded
        hw_reqs = dictionary.get('args')[3]
        memory_req = hw_reqs.get('args')[0]
        v_cpu_req = hw_reqs.get('args')[1].get('args')[0]
        mhz_req = hw_reqs.get('args')[1].get('args')[1]
        
        function = PlacedFunction(function_id, node_id, sw_reqs, memory_req, v_cpu_req, mhz_req, is_guard)
        
        return { 
            function_id : function
        }
    elif expression == 'if':
        guard = rec_parse_placement(dictionary.get('args')[0], placement, True)
        c1 = rec_parse_placement(dictionary.get('args')[1], placement, False)
        c2 = rec_parse_placement(dictionary.get('args')[2], placement, False)
        
        placement.update(guard)
        placement.update(c1)
        placement.update(c2)
        
        return placement
    elif expression == 'par':
        c1 = rec_parse_placement(dictionary.get('args')[0][0], placement, False)
        c2 = rec_parse_placement(dictionary.get('args')[0][1], placement, False)
        
        placement.update(c1)
        placement.update(c2)
        
        return placement
    elif expression == 'seq':
        c1 = rec_parse_placement(dictionary.get('args')[0], placement, False)
        c2 = rec_parse_placement(dictionary.get('args')[1], placement, False)
        
        placement.update(c1)
        placement.update(c2)
        
        return placement


def parse_placement(prolog_placement : dict) -> dict[str, PlacedFunction] :
    orchestration_id = prolog_placement["OrchestrationId"] # TODO facci qualcosa

    return rec_parse_placement(prolog_placement['Placement'], {}, False)

# functions used to retrieve application chain 

def rec_build_app_chain(dictionary: dict, dependencies: dict, caller):
    expression = dictionary['functor']
    
    if expression == 'fp':
        function : str = dictionary.get('args')[0]
        
        return function, function, expression
    elif expression == 'if':
        guard = dictionary.get('args')[0].get('args')[0]
        c11, c12, exp_type1 = rec_build_app_chain(dictionary.get('args')[1], dependencies, guard)
        c21, c22, exp_type2 = rec_build_app_chain(dictionary.get('args')[2], dependencies, guard)
        
        dependencies[guard] = caller
        dependencies[c11] = guard
        dependencies[c21] = guard
        return c12, c22, expression

    elif expression == 'par':
        c11, c12, exp_type1 = rec_build_app_chain(dictionary.get('args')[0][0], dependencies, caller)
        c21, c22, exp_type2 = rec_build_app_chain(dictionary.get('args')[0][1], dependencies, caller)

        return1 = (c11, c12) if exp_type1 not in ['fp', 'seq'] else c12
        return2 = (c21, c22) if exp_type2 not in ['fp', 'seq'] else c22
            
        return return1, return2, expression

    elif expression == 'seq':
        c11, c12, exp_type1 = rec_build_app_chain(dictionary.get('args')[0], dependencies, caller)
        c21, c22, exp_type2 = rec_build_app_chain(dictionary.get('args')[1], dependencies, c12)

        if c21 not in dependencies and type(c21) is not tuple:
            if exp_type1 == 'seq':
                dependencies[c21] = c12
            else:
                dependencies[c21] = (c11, c12) if c11 != c12 else c11
        if c22 not in dependencies and type(c22) is not tuple:
            if exp_type1 == 'seq':
                dependencies[c22] = c12
            else:
                dependencies[c22] = (c11, c12) if c11 != c12 else c11
        if c11 not in dependencies and type(c11) is not tuple:
            dependencies[c11] = caller
        if c12 not in dependencies and type(c12) is not tuple:
            dependencies[c12] = caller
        
        return1 = (c11, c12) if exp_type1 != 'fp' else c12
        return2 = (c21, c22) if exp_type2 != 'fp' else c22
            
        return return1, return2, expression


def unpack_nested_tuples(t: tuple):
    elements = list(t)
    to_return = []
    for elem in elements:
        if type(elem) is tuple:
            result = unpack_nested_tuples(elem)
            to_return += result
        else:
            to_return.append(elem)
    
    return to_return


def build_app_chain(prolog_placement: dict) -> dict[str, str]:
    #orchestration_id = placement["OrchestrationId"]  # TODO facci qualcosa

    dependencies = {}

    _ = rec_build_app_chain(prolog_placement['Placement'], dependencies, None)

    to_return = {}

    keys = dependencies.keys()
    for key in keys:
        if type(key) is not tuple:
            value = dependencies.get(key)
            if type(value) is tuple:
                new_value = unpack_nested_tuples(value)
                to_return[key] = new_value
            else:
                new_value = [value]
                to_return[key] = new_value

    return to_return
