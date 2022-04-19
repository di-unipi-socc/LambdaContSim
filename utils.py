# return a list of functions that can be executed (their dependencies has been already executed)

def get_ready_functions(function_dependencies: dict) -> list[str]:
    to_return = []
    functions = function_dependencies.keys()
    for fun in functions:
        dependencies = function_dependencies.get(fun)
        if len(dependencies) == 0 or None in dependencies:
            to_return.append(fun)
    
    return to_return

def delete_executed_function(function_dependencies: dict, finished_function):
    
    function_dependencies.pop(finished_function)
    
    functions = function_dependencies.keys()
    for fun in functions:
        dependencies : list = function_dependencies.get(fun)
        if finished_function in dependencies:
            dependencies.remove(finished_function)
    