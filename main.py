import re
import sys, random
from datetime import datetime
from swiplserver import PrologMQI
import json
from config import parse_config
from infrastructure.infrastructure import Infrastructure
from infrastructure.node import Node
from application.function import PlacedFunction
from math import inf
import os
import shutil
import math
import config
from orchestration.orchestrator import Orchestrator


def place(dictionary : dict, placement : dict):
    expression = dictionary['functor']
    if expression == 'fp':
        function_id = dictionary.get('args')[0]
        node_id = dictionary.get('args')[5]
        sw_reqs = dictionary.get('args')[2]
        hw_reqs = dictionary.get('args')[3]
        memory_req = hw_reqs.get('args')[0]
        v_cpu_req = hw_reqs.get('args')[1].get('args')[0]
        mhz_req = hw_reqs.get('args')[1].get('args')[1]
        function = PlacedFunction(function_id, node_id, sw_reqs, memory_req, v_cpu_req, mhz_req)
        return { 
            function_id : function
        }
    elif expression == 'if':
        guard = place(dictionary.get('args')[0], placement)
        c1 = place(dictionary.get('args')[1], placement)
        c2 = place(dictionary.get('args')[2], placement)
        placement.update(guard)
        placement.update(c1)
        placement.update(c2)
        return placement
    elif expression == 'par':
        c1 = place(dictionary.get('args')[0][0], placement)
        c2 = place(dictionary.get('args')[0][1], placement)
        placement.update(c1)
        placement.update(c2)
        return placement
    elif expression == 'seq':
        c1 = place(dictionary.get('args')[0], placement)
        c2 = place(dictionary.get('args')[1], placement)
        placement.update(c1)
        placement.update(c2)
        return placement


def dipendenze(dictionary: dict, dependencies: dict, caller):
    expression = dictionary['functor']
    #print(dependencies)
    #print(expression)
    if expression == 'fp':
        function : str = dictionary.get('args')[0]
        #dependencies[function] = None
        return function, function, expression
    elif expression == 'if':
        guard = dictionary.get('args')[0].get('args')[0]
        c11, c12, exp_type1 = dipendenze(dictionary.get('args')[1], dependencies, guard)
        c21, c22, exp_type2 = dipendenze(dictionary.get('args')[2], dependencies, guard)
        #print("guard %s c1 %s c2 %s" % (guard, c1, c2))
        #print("IF c11 %s c12 %s c21 %s c22 %s" % (c11, c12, c21, c22))
        dependencies[guard] = caller
        dependencies[c11] = guard
        dependencies[c21] = guard
        return c12, c22, expression

    elif expression == 'par':
        c11, c12, exp_type1 = dipendenze(dictionary.get('args')[0][0], dependencies, caller)
        c21, c22, exp_type2 = dipendenze(dictionary.get('args')[0][1], dependencies, caller)
        #dependencies[c11] = caller
        #dependencies[c21] = caller

        return1 = (c11, c12) if exp_type1 not in ['fp', 'seq'] else c12
        return2 = (c21, c22) if exp_type2 not in ['fp', 'seq'] else c22
            
        return return1, return2, expression
        #return (c11, c12) if c11 != c12 else c11, (c21, c22) if c21 != c22 else c21, expression
        return c12, c22, expression

    elif expression == 'seq':
        c11, c12, exp_type1 = dipendenze(dictionary.get('args')[0], dependencies, caller)
        c21, c22, exp_type2 = dipendenze(dictionary.get('args')[1], dependencies, c12)
        #print("SEQ c11 %s c12 %s c21 %s c22 %s" % (c11, c12, c21, c22))
        

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
        #return (c11, c12) if c11 != c12 else c11, (c21, c22) if c21 != c22 else c21


def build_placement(prolog_placement : dict) -> dict[str, PlacedFunction] :
    orchestration_id = prolog_placement["OrchestrationId"] # TODO facci qualcosa

    return place(prolog_placement['Placement'], {})

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

def find_dependencies(prolog_placement: dict) -> dict[str, str]:
    #orchestration_id = placement["OrchestrationId"]  # TODO facci qualcosa

    dependencies = {}

    _ = dipendenze(prolog_placement['Placement'], dependencies, None)

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


def take_decision(probability : float) -> bool:

    return random.random() < probability


# Entry point of the simulator
# :param: application
# :param: infrastructure
# :param: trigger_prob probability of a new placement request
# :param: num_of_epochs
def main(argv):

    secfaas2fog_folder = './SecFaas2Fog'
    secfaas2fog_abs_path = os.path.abspath(
        os.path.expanduser(os.path.expandvars(secfaas2fog_folder)))

    # defaults .pl path
    placer_path = os.path.join(secfaas2fog_abs_path,'placer.pl')
    application_path = os.path.join(secfaas2fog_abs_path, 'application.pl')
    infrastructure_path = os.path.join(secfaas2fog_abs_path, 'infrastructure.pl')

    # statistical variables
    # placement results is a list of objects like {start: time, end : time, success : bool}
    placement_results : list = []

    # config path
    config_path = None

    error = False
    # parse command line arguments
    for i in range(0, len(argv)-1, 2):
        if error:
            break
        option = argv[i]
        option_value = argv[i+1]
        if (option == '-c'):
            # path of a valid config
            error = not os.path.isfile(option_value)
            config_path = option_value

    if len(argv) != 2 or error:

        print("Usage:")
        print("python3 main.py -c <config.yaml path>")
        return 0
    
    parse_config(config_path)
    
    # TODO

    # get config file from command line

    # scan config file

    # save application and infrastructure files into default paths
    
    # TODO NOW WE HAVE ONLY 1 APP
    #print(config.num_of_epochs)
    shutil.copy(config.applications[0]['path'], application_path)
    shutil.copy(config.infrastructure_temp_path, infrastructure_path)

    # instance infrastructure
    nodes : dict[str, Node] = {}
    latencies : dict[str, dict[str, ( int, bool )]] = {}
    # TODO check errors on file opening
    node_pattern = r'^node\(([^,]+),([^,]+),(\[.*?\]),(\[.*?\]),\(([^,]+),([^,]+),([^\)]+)\)\)\.*'
    latency_pattern = r'^latency\(([^,]+),([^,]+),([^,]+)\)\.*'

    other_lines = []

    with open(infrastructure_path) as f:
        lines = f.readlines()

        for line in lines:
            if line.startswith('node'):
                line = line.replace(' ', '')
                #print(line)
                match = re.match(node_pattern, line).groups()

                node_id = match[0]
                provider = match[1]
                security_caps = match[2].replace('[','').replace(']','').split(',')
                software_caps = match[3].replace('[','').replace(']','').split(',')
                memory = inf if match[4] == 'inf' else int(match[4])
                v_cpu = inf if match[5] == 'inf' else int(match[5])
                mhz = inf if match[6] == 'inf' else int(match[6])

                node = Node(node_id, provider, security_caps, software_caps, memory, v_cpu, mhz)
                nodes[node_id] = node

                # create latency index for the node
                latencies[node_id] = {}

            elif line.startswith('latency'):
                line = line.replace(' ', '')
                match = re.match(latency_pattern, line).groups()

                first_node = match[0]
                second_node = match[1]
                latency = int(match[2])
                
                dictionary = latencies.get(first_node)
                dictionary[second_node] = { 'latency' : latency, 'available' : True }

            elif not line.startswith('%'):
                # save other crucial informations
                # discarding comments
                other_lines.append(line)
        
        #print(other_lines)
        #instance infrastructure
        infrastructure = Infrastructure(nodes, latencies, other_lines)

    # instance application TODO REMOVE
    '''
    functions: list[Function] = []
    # TODO check errors on file opening
    pattern = r'^functionReqs\(([^,]+),(\[.*?\]),\(([^,]+),([^,]+),([^\)]+)\),(\[.*?\])*'
    with open(application_path) as f:
        lines = f.readlines()

        for line in lines:
            if line.startswith('functionReqs'):
                line = line.replace(' ', '')
                #print(line)
                match = re.match(pattern, line).groups()

                function_id = match[0]
                software_reqs = match[1].replace('[','').replace(']','').split(',')
                memory = inf if match[2] == 'inf' else int(match[2])
                v_cpu = inf if match[3] == 'inf' else int(match[3])
                mhz = inf if match[4] == 'inf' else int(match[4])
                # service requirements not read

                function = Function(function_id, software_reqs, memory, v_cpu, mhz)
                functions.append(function)
    '''


    # declare Prolog variable
    # once means that we take the first of the results
    secfaas2fog_command = "once(secfaas2fog(OrchestrationId, Placement))."

    for index in range(0, config.num_of_epochs):


        # we want to trigger a new placement request?
        trigger = take_decision(config.placement_trigger_probability)

        # node crash trigger
        node_crash_trigger = take_decision(0.2)

        node_resurrection_trigger = take_decision(0.2)

        # link crash trigger
        link_crash_trigger = take_decision(0.3)

        link_resurrection_trigger = take_decision(0.3)

        if (node_crash_trigger):
            print("NODE CRASH")
            infrastructure.simulate_node_crash()
        
        elif node_resurrection_trigger:
            print("NODE RESURRECT")
            infrastructure.simulate_node_resurrection()
        
        if (link_crash_trigger):
            print("LINK CRASH")
            infrastructure.simulate_link_crash()
        
        elif link_resurrection_trigger:
            print("LINK RESURRECT")
            infrastructure.simulate_link_resurrection()

        if (trigger) :

            # call secFaas2Fog
            # it will reply with a valid placement iff application can be placed
            placement = None
            application_can_be_placed = False
            start_time = datetime.now()
            with PrologMQI(prolog_path_args=[
                    "-s", placer_path
            ]) as mqi:
                with mqi.create_thread() as prolog_thread:
                    query = prolog_thread.query(secfaas2fog_command)
                    end_time = datetime.now()

                    if isinstance(query, list):
                        placement = query[0] # should be a dictionary
                        #print(placement)

                        # check if the placement is a dictionary
                        if placement is not None and isinstance(placement, dict):
                            function_chain = find_dependencies(placement)
                            placement = build_placement(placement)
                            #print(placement)
                            #print(function_chain)

                        application_can_be_placed = True
                    else:
                        print("Placement failed")

            placement_data : dict = {
                'start' : start_time,
                'end' : end_time,
                'success' : application_can_be_placed
            }

            placement_results.append(placement_data)

            if (application_can_be_placed) :
                pass

                # create application instance
                # TODO actually we have 1 application so it is defined above

                # place application over the infrastructure (update nodes capabilities: memory, number of vCPUs )
                functions = placement.keys()
                for function in functions:
                    node_id = placement[function].node_id
                    node = nodes[node_id]
                    #print("%s %s" % (function.id, node_id))
                    node.take_resources(memory = placement[function].memory, v_cpu = placement[function].v_cpu) # TODO functions are not padded

                # launch application for a determined amount of time
                thread = Orchestrator("Placement", 1000 + index, nodes, function_chain, placement)
                thread.start()

            # update infastructure.pl
            lines = []

            nodes_keys = nodes.keys()
            for key in nodes_keys:
                node = nodes[key]
                # if the node is not available, don't write it
                if node.available:
                    node_string = "node(" + node.id + ", " + node.provider + ", ["
                    for sec_cap in node.security_capabilites:
                        node_string += sec_cap + ","
                    node_string = node_string.removesuffix(",")
                    node_string += "], ["
                    for sw_cap in node.software_capabilites:
                        node_string += sw_cap + ","
                    node_string = node_string.removesuffix(",")
                    node_string += "], (" + str(node.memory) + "," + str(node.v_cpu) + "," + str(node.mhz) + ")).\n"
                    #print(node_string)
                    lines.append(node_string)

            # write non-saved data into file
            for line in infrastructure.other_data:
                lines.append(line)
            
            # write latencies informations
            first_keys = infrastructure.latencies.keys()
            for f_key in first_keys:
                first_key_links = infrastructure.latencies.get(f_key).keys()
                for s_key in first_key_links:
                    latency = infrastructure.latencies.get(f_key).get(s_key)['latency']
                    available = infrastructure.latencies.get(f_key).get(s_key)['available']
                    # write iff link is available
                    if available:
                        latency_string = 'latency(' + f_key + ', ' + s_key + ', ' + str(latency) + ').\n'
                        lines.append(latency_string)

            # overwrite file
            with open(infrastructure_path, 'w') as f:
                for line in lines:
                    f.write(line)

    # statistical prints

    num_of_placement = 0
    successess = 0
    sum = 0
    for result in placement_results:
        print("Placement #%d:" % num_of_placement)
        print("\tSecFaas2Fog start: ", result['start'])
        print("\tSecFaas2Fog end: ", result['end'])
        end_millisec = result['end'].timestamp() * 1000
        start_millisec = result['start'].timestamp() * 1000
        sum += end_millisec - start_millisec
        print("\tPlaced? ", result['success'])
        if result['success'] :
            successess += 1
        num_of_placement += 1

    print("Number of placements: %d" % len(placement_results))
    print("Average time of SecFaas2Fog placement: " + str(float(f'{sum/num_of_placement:.2f}')) + " milliseconds")
    print("Successess: %d" % successess)

    print("Writing report file...")

    # TODO write report file
    

    print("Done!")


if __name__ == "__main__":
    main(sys.argv[1:])
