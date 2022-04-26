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

def take_decision(probability : float) -> bool:

    import random
    return random.random() < probability
    