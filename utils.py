# return a list of functions that can be executed (their dependencies has been already executed)

def get_ready_functions(application_chain: dict) -> list[str]:
    to_return = []
    functions = application_chain.keys()
    for fun in functions:
        dependencies = application_chain.get(fun)
        if len(dependencies) == 0 or None in dependencies:
            to_return.append(fun)
    
    return to_return

def get_next_functions_by_id(application_chain: dict, function_id : str) -> list[str]:
    to_return = []
    functions = application_chain.keys()
    for fun in functions:
        dependencies = application_chain.get(fun)
        if function_id in dependencies:
            to_return.append(fun)
    
    return to_return

def delete_executed_function(application_chain: dict, finished_function):
    
    application_chain.pop(finished_function)
    
    functions = application_chain.keys()
    for fun in functions:
        dependencies : list = application_chain.get(fun)
        if finished_function in dependencies:
            dependencies.remove(finished_function)

def delete_functions_chain_by_id(application_chain: dict, function_to_remove) -> list:
    
    application_chain.pop(function_to_remove)

    dept_to_remove = []
    
    functions = application_chain.keys()
    for fun in functions:
        dependencies : list = application_chain.get(fun)
        if function_to_remove in dependencies:
            dependencies.remove(function_to_remove)
            
            # if it was the only dependency, remove the dependent
            if len(dependencies) == 0:
                dept_to_remove.append(fun)
    
    result = [function_to_remove]

    for fun in dept_to_remove:
        result += delete_functions_chain_by_id(application_chain, fun)
    
    return result


def get_recursive_dependents(start_function : str, application_chain: dict) -> list:
    
    dependents = []

    functions = application_chain.keys()
    for fun in functions:
        dependencies : list = application_chain.get(fun)
        if start_function in dependencies:
            dependents.append(fun)

    to_return = dependents

    for fun in dependents:
        to_return += get_recursive_dependents(fun, application_chain)
    
    return list(set(to_return))


def rec(boh : dict, function, chain, level):

    list = get_next_functions_by_id(chain, function)

    old_level = boh[function] if function in boh.keys() else 0

    boh[function] = max(old_level, level)

    if len(list) > 0:
        for fun in list:
            rec(boh, fun, chain, level + 1)


def get_oldest(interested_functions : list, original_chain : dict[str, list]):
    print(original_chain)
    other = {}
    rec(other, 'fLogin', original_chain, 0)
    print(other)

    levelled_fun : dict[int, list] = {}

    keys = other.keys()
    for key in keys:
        levelled_fun[other[key]] = []
    for key in keys:
        levelled_fun[other[key]].append(key)
    
    print(levelled_fun)

    # find the oldest between interested functions
    oldest = interested_functions[0]
    for function in interested_functions:
        if function == oldest:
            continue
        if other[function] < other[oldest]:
            oldest = function
    
    found = False

    oldest_list = [oldest]
    print(interested_functions)
    
    while not found:
        for oldest in oldest_list:
            print(oldest)
            # get dependent functions from the oldest
            oldest_dependents = get_recursive_dependents(oldest, original_chain)

            # if all functions are dependants of the oldest, then we finished
            found = True
            for function in interested_functions:
                if function == oldest:
                    continue
                if function not in oldest_dependents:
                    print(function)
                    print(oldest_dependents)
                    found = False
                    break
            
            if found:
                return oldest
        
        # search a new oldest
        oldest_level = other[oldest]
        oldest_level -= 1
        oldest_list = levelled_fun[oldest_level]

    return None


def take_decision(probability : float) -> bool:

    import random
    return random.random() < probability
    