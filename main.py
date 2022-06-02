import sys
from datetime import datetime
from swiplserver import PrologError, PrologMQI
import json
from application.application import Application, ApplicationState
from application.placed_function import FunctionState, PlacedFunction
from config import parse_config
from generate_infrastructure import generate_infrastructure
from infrastructure.infrastructure import Infrastructure
from infrastructure.logical_infrastructure import LogicalInfrastructure
from infrastructure.node import NodeCategory
import os
import shutil
import config
from infrastructure.physical_infrastructure import PhysicalInfrastructure
from orchestration.orchestrator import Orchestrator
import logs
import logging
from placement import PlacementType, build_app_chain, get_placement_query, parse_placement
import simpy
import global_variables as g
from utils import get_recursive_dependents, is_edge_part, take_decision, get_oldest
import random
import networkx as nx

# Statistical variables

applications_stats : dict = {}
node_events : list = []
node_stats : dict[str, list] = {}
link_events : list = []


def print_usage():
    ''' Print application usage message'''
    print('Usage: %s [<options>]' % os.path.basename(sys.argv[0]))
    print('       %s [-h|--help] to show this help message' % os.path.basename(sys.argv[0]))
    print('\nOptions:')
    print('-c <config file> application config (default config.yaml)')


def dump_infrastructure(infrastructure : Infrastructure, output_filename: str):
    ''' Dump infrastructure on a given file '''

    lines = []

    nodes = infrastructure.nodes

    graph_nodes = infrastructure.graph.nodes(data=True)
    for (node_id, node_data) in graph_nodes:
        node = nodes[node_id]
        # if the node is not available, don't write it
        if node_data['available']:
            node_string = f"node({node.id}, {node.category.value}, {node.provider}, ["
            for sec_cap in node.security_capabilites:
                node_string += sec_cap + ", "
            node_string = node_string.removesuffix(", ")
            node_string += "], ["
            for sw_cap in node.software_capabilites:
                node_string += sw_cap + ", "
            node_string = node_string.removesuffix(", ")
            node_string += f"], ({str(node.memory)}, {str(node.v_cpu)}, {str(node.mhz)}))."
            lines.append(node_string)

    # event generators
    for event_gen in infrastructure.event_generators:
        string = f'eventGenerator({event_gen.generator_id}, ['
        for event, _ in event_gen.events:
                string += event + ", "
        string = string.removesuffix(", ")
        string += f'], {event_gen.source_node}).'
        lines.append(string)
    
    # services
    for service in infrastructure.services:
        string = f'service({service.id}, {service.provider}, {service.type}, {service.deployed_node}).'
        lines.append(string)

    # we need these lines in order to declare links as unidirectionals
    lines.append('link(X,X,0).')
    lines.append('link(X,Y,L) :- dif(X,Y), (latency(X,Y,L);latency(Y,X,L)).')
    
    # get crashed nodes
    crashed_nodes = infrastructure.crashed_nodes
    # get crashed links
    crashed_links = infrastructure.crashed_links
    
    # write latencies informations
    latencies = infrastructure.latencies
    for node1 in latencies.keys():
        # don't write a link with a crashed node
        if node1 in crashed_nodes:
            continue
        node2list : dict = latencies[node1]
        for node2 in node2list.keys():
            # don't write a link with a crashed node
            if node2 in crashed_nodes:
                continue
            # don't write a crashed link
            if not (node1, node2) in crashed_links and not (node2, node1) in crashed_links:
                string = f'latency({node1}, {node2}, {latencies[node1][node2]}).'
                lines.append(string)

    # overwrite file
    with open(output_filename, 'w') as f:
        for line in lines:
            f.write(line+'\n')


def get_raw_placement(placement_type : PlacementType, orchestration_id : str, generator_id : str = None, starting_function : str = None, starting_nodes : list[str] = None):
    '''
    Returns the application placement found by SecFaas2Fog.
    Returns a 3-tuple (placement, execution start, execution end):
    placement is None if query is not good
    placement is an empty dictionary if the application cannot be placed
    placement is a valid dictionary if the application can be placed
    '''
    
    logger = logs.get_logger()

    # prepare the query
    query = ""

    # if we need a replacement, we have to pass starting function and starting node
    if placement_type in [PlacementType.PADDED_REPLACEMENT, PlacementType.UNPADDED_REPLACEMENT]:
        query = get_placement_query(
            placement_type=placement_type,
            max_placement_time=config.sim_max_placement_time,
            orchestration_id=orchestration_id,
            starting_function=starting_function,
            starting_nodes=starting_nodes
        )
    elif placement_type in [PlacementType.PADDED_PLACEMENT, PlacementType.UNPADDED_PLACEMENT]:
        query = get_placement_query(
            placement_type=placement_type,
            max_placement_time=config.sim_max_placement_time,
            orchestration_id=orchestration_id,
            generator_id=generator_id
        )
    
    if query is None:
        return None, None, None
    
    # try to place this app with SecFaas2Fog

    # it will reply with a valid placement iff application can be placed
    raw_placement = None
    query_result = False

    with PrologMQI(prolog_path_args=[
            "-s", g.secfaas2fog_placer_path
    ]) as mqi:
        with mqi.create_thread() as prolog_thread:

            try:

                # save SecFaas2Fog starting time
                start_time = datetime.now()
            
                query_result = prolog_thread.query(query)
            
            except PrologError:
                logger.error("Prolog execution failed")
            
            finally:
                # save SecFaas2Fog finish time
                end_time = datetime.now()

    if query_result != False and isinstance(query_result, list):
                    
        raw_placement = query_result[0] # it is a dictionary
        
        return raw_placement, start_time, end_time
    
    return {}, start_time, end_time
    

def place_application(
    application_name : str,
    config_application : dict,
    generator_id : str,
    infrastructure : Infrastructure,
    epoch : int
):

    # get the logger
    logger = logs.get_logger()

    # application should be padded?
    placement_type = PlacementType.PADDED_PLACEMENT
    if not config.sim_use_padding:
        placement_type = PlacementType.UNPADDED_PLACEMENT

    # try to place this app with SecFaas2Fog

    # it will reply with a valid placement iff application can be placed
    raw_placement, start_time, end_time = get_raw_placement(
        placement_type=placement_type,
        orchestration_id=config.applications[application_name]['orchestration_id'],
        generator_id=generator_id
    )

    application_can_be_placed = False

    if raw_placement is None:
        logger.critical("Query is None")  
    elif raw_placement == {}:
        logger.info("Placement failed for %s", application_name)
    else:
        application_chain = build_app_chain(raw_placement)
        placement = parse_placement(raw_placement)
        
        # calculate for each function its dependency nodes
        functions = placement.keys()
        for function_name in functions:
            placed_function = placement[function_name]
            dependencies = application_chain[function_name]
            if len(dependencies) == 0:
                # starting function
                # get the node where the generator is placed
                generator_node = [gen for gen in infrastructure.event_generators if gen.generator_id == generator_id][0].source_node
                placed_function.previous_nodes.append(generator_node)
            else:
                for dependency in dependencies:
                    node_id = placement[dependency].node_id
                    if node_id not in placed_function.previous_nodes:
                        placed_function.previous_nodes.append(node_id)
        
        #print(placement)
        #print(application_chain)

        application_can_be_placed = True

        logger.info("Placement found for %s", application_name)

    if application_name not in applications_stats.keys():
        applications_stats[application_name] = {}
        applications_stats[application_name]['placements'] = []

    # normal placement
    placement_data : dict = {
        'event' : 'placement',
        'nodes' : [generator_id],
        'links' : [],
        'start' : start_time,
        'end' : end_time,
        'epoch' : epoch,
        'success' : application_can_be_placed
    }

    applications_stats[application_name]['placements'].append(placement_data)

    if application_can_be_placed :

        # create application instance
        application_obj = Application(
            application_name,
            config_application['filename'],
            config_application['orchestration_id'],
            application_chain,
            placement,
            infrastructure.nodes
        )
        
        # place application over the infrastructure (update nodes capabilities: memory, number of vCPUs )
        functions = placement.keys()
        for function_id in functions:
            node_id = placement[function_id].node_id
            node_obj = infrastructure.nodes[node_id]
            
            # take resources from the node
            node_obj.take_resources(memory = placement[function_id].memory, v_cpu = placement[function_id].v_cpu)
        
        return application_obj
    
    return None


def replace_application(
    application_obj : Application,
    starting_function : str,
    starting_nodes : list[str],
    crashed_nodes : list,
    crashed_link : list,
    infrastructure : Infrastructure,
    epoch : int
):
    # get the logger
    logger = logs.get_logger()

    # application should be padded?
    placement_type = PlacementType.PADDED_REPLACEMENT
    if not config.sim_use_padding:
        placement_type = PlacementType.UNPADDED_REPLACEMENT

    # get application name
    application_name = application_obj.name

    # try to place this app with SecFaas2Fog

    # it will reply with a valid placement iff application can be placed
    raw_placement, start_time, end_time = get_raw_placement(
        placement_type=placement_type,
        starting_function=starting_function,
        starting_nodes=starting_nodes,
        orchestration_id=config.applications[application_name]['orchestration_id']
    )

    application_can_be_placed = False

    if raw_placement is None:
        logger.critical("Query is None")  
    elif raw_placement == {}:
        logger.info("Replacement failed for %s", application_obj.id)
    else:
        new_application_chain = build_app_chain(raw_placement)
        new_placement = parse_placement(raw_placement)
        
        #print(new_placement)
        #print(new_application_chain)

        # calculate for each function its dependency nodes
        functions = new_placement.keys()
        for function_name in functions:
            new_placed_function = new_placement[function_name]
            new_function_dependencies = new_application_chain[function_name]
            if len(new_function_dependencies) == 0:
                # start function
                new_placed_function.previous_nodes += starting_nodes
            else:
                for dependency in new_function_dependencies:
                    
                    node_id = new_placement[dependency].node_id
                    
                    if node_id not in new_placed_function.previous_nodes:
                        new_placed_function.previous_nodes.append(node_id)

        application_can_be_placed = True

        logger.info("Replacement found for %s", application_obj.id)

    if application_name not in applications_stats.keys():
        applications_stats[application_name] = {}
        applications_stats[application_name]['placements'] = []

    # normal placement
    placement_data : dict = {
        'event' : 'crash',
        'nodes' : crashed_nodes,
        'links' : crashed_link,
        'start' : start_time,
        'end' : end_time,
        'epoch' : epoch,
        'success' : application_can_be_placed
    }

    applications_stats[application_name]['placements'].append(placement_data)

    if application_can_be_placed :

        # update the application replacing old placed functions with new ones
        functions = new_placement.keys()
        for function_id in functions:
            application_obj.placement[function_id] = new_placement[function_id]

        # place new functions over the infrastructure (update nodes capabilities: memory, number of vCPUs )
        for function_id in functions:
            node_id = new_placement[function_id].node_id
            node_obj = infrastructure.nodes[node_id]
            
            # take resources from the node
            node_obj.take_resources(memory = new_placement[function_id].memory, v_cpu = new_placement[function_id].v_cpu)
        
        return True, new_application_chain
    
    return False, None


def simulation(
    env : simpy.Environment,
    steps : int,
    infrastructure : Infrastructure
    ):
    
    # get logger
    logger = logs.get_logger()

    # list of applications
    list_of_applications : list[Application] = []

    for step_number in range(0, steps):
        
        # print the step
        logger.info("--- STEP %d ---", step_number)

        # PLACEMENT PHASE

        # for each event generator
        for event_generator in infrastructure.event_generators:

            # generator is triggering?
            generator_triggered = take_decision(config.event_generator_trigger_probability)

            if generator_triggered:
                logger.info(f'Generator {event_generator.generator_id} triggered')

                # get the list of triggered events
                triggered_events = []
                for event, event_probability in event_generator.events:
                    
                    # event of that generator is triggering?
                    event_triggered = take_decision(event_probability)

                    if event_triggered:
                        triggered_events.append(event)

                # for each application, check if it is triggered by one of these events
                for application_name in config.applications:

                    config_application = config.applications[application_name]

                    if config_application['trigger_event'] in triggered_events:

                        # try to place the application
                        logger.info(f"Event {config_application['trigger_event']} ({event_generator.generator_id}) triggered {application_name}")
                        
                        # get application path
                        application_filename = config_application['filename']
                        application_path = os.path.join(g.applications_path, application_filename)

                        # save application file into default path
                        shutil.copy(application_path, g.secfaas2fog_application_path)

                        # place
                        application_obj = place_application(
                            application_name,
                            config_application,
                            event_generator.generator_id,
                            infrastructure,
                            step_number
                        )

                        if application_obj is not None:
                            # launch application
                            thread = Orchestrator(env=env, application=application_obj)
                            thread.start()

                            # add application into a list
                            list_of_applications.append(application_obj)

                        # update infastructure.pl
                        dump_infrastructure(infrastructure, g.secfaas2fog_infrastructure_path)
                

        # CRASH/RESURRECTION PHASE

        # reset variables
        crashed_node_id = {}
        resurrected_node_id = {}
        first_node = None
        second_node = None
        first_crashed_node = None
        second_crashed_node = None
        
        # list of replacing applications
        apps_just_added : list[Application] = []

        # NODE crash
        for category in ['cloud', 'fog', 'edge']:
            
            node_crashed = take_decision(config.infr_node_crash_probability[category])

            node_resurrected = take_decision(config.infr_node_resurrection_probability[category])

            crashed_node_id[category] = None

            if node_crashed:
                crashed_node_id[category] = infrastructure.simulate_node_crash(NodeCategory.from_string(category))
                
                if crashed_node_id[category] is not None:
                    logger.info("Node %s crashed", crashed_node_id[category])
                    
                    # add event to the list
                    event = {
                        'type' : 'crash',
                        'node_id' : crashed_node_id[category],
                        'epoch' : step_number
                    }
                    node_events.append(event)
            
            if node_resurrected:
                if crashed_node_id[category] is not None:
                    # node which just crashed can't resurrect in the same epoch
                    resurrected_node_id = infrastructure.simulate_node_resurrection(NodeCategory.from_string(category), crashed_node_id[category])
                else:
                    resurrected_node_id = infrastructure.simulate_node_resurrection(NodeCategory.from_string(category))
                
                if resurrected_node_id is not None:
                    logger.info("Node %s resurrected", resurrected_node_id)

                    # add event to the list
                    event = {
                        'type' : 'resurrection',
                        'node_id' : resurrected_node_id,
                        'epoch' : step_number
                    }
                    node_events.append(event)

        crashed_nodes = list(crashed_node_id.values())

        # LINK crash
        link_crashed = take_decision(config.infr_link_crash_probability)

        link_resurrected = take_decision(config.infr_link_resurrection_probability)

        crashed_link = []

        if link_crashed:
            first_crashed_node, second_crashed_node = infrastructure.simulate_link_crash()
            
            if first_crashed_node != None and second_crashed_node != None:
                logger.info("Link %s <-> %s crashed", first_crashed_node, second_crashed_node)

                # add event to the list
                event = {
                    'type' : 'crash',
                    'first_node_id' : first_crashed_node,
                    'second_node_id' : second_crashed_node,
                    'epoch' : step_number
                }
                link_events.append(event)

                crashed_link = [first_crashed_node, second_crashed_node]
        
        if link_resurrected:

            if first_node is not None and second_node is not None:
                link_to_exclude = (first_crashed_node, second_crashed_node)
                # link which just crashed can't resurrect in the same epoch
                first_node, second_node = infrastructure.simulate_link_resurrection(link_to_exclude)
            else:
                first_node, second_node = infrastructure.simulate_link_resurrection()

            if first_node != None and second_node != None:
                logger.info("Link %s <-> %s resurrected", first_node, second_node)

                # add event to the list
                event = {
                    'type' : 'resurrection',
                    'first_node_id' : first_node,
                    'second_node_id' : second_node,
                    'epoch' : step_number
                }
                link_events.append(event)

        # there are affected applications?
        for application_obj in list_of_applications:

            # completed or canceled apps are not interesting
            if application_obj.state in [ApplicationState.COMPLETED, ApplicationState.CANCELED]:
                continue

            # list of functions interested by the crash
            interested_functions = set()
            
            for function_name in application_obj.placement:
                placed_function : PlacedFunction = application_obj.placement[function_name]

                # NODE crash
                # check if there is at least one function deployed in the crashed nodes
                # check only waiting and running functions

                if node_crashed:
                
                    if placed_function.state in [FunctionState.WAITING, FunctionState.RUNNING]:
                        if placed_function.node_id in crashed_nodes:
                            interested_functions.add(placed_function.id)

                            # interrupt the function if it is running
                            if placed_function.state == FunctionState.RUNNING:
                                
                                application_obj.function_processes[placed_function.id].action.interrupt()
                
                # LINK crash
                # if there is a waiting function2 deployed on nodeY
                # for any function1 deployed on nodeX
                # where function2 is dependent on function1
                # check if the link (node1, node2) belongs to the path from nodeX to nodeY

                if link_crashed:
                
                    if placed_function.state == FunctionState.WAITING:
                        node_y = placed_function.node_id
                        previous_nodes = placed_function.previous_nodes
                        for node_x in previous_nodes:
                            path = nx.dijkstra_path(infrastructure.graph, node_x, node_y)
                            if is_edge_part(path, first_crashed_node, second_crashed_node):
                                interested_functions.add(placed_function.id)
        
            if len(interested_functions) > 0:
                logger.info("Application %s needs a replacement", application_obj.id)

                # find the oldest relative among them
                start_function = get_oldest(list(interested_functions), application_obj.original_chain)

                dependents_functions = get_recursive_dependents(start_function, application_obj.chain)
                
                starting_nodes = application_obj.placement[start_function].previous_nodes

                # release all resources of dependents functions
                for function_name in dependents_functions:
                    function = application_obj.placement[function_name]
                    node_id = function.node_id
                    node_obj = application_obj.infrastructure_nodes[node_id]
                    node_obj.release_resources(function.memory, function.v_cpu)

                    logger.info("Application %s - Function %s has been canceled", application_obj.id, function.id)
                    function.state = FunctionState.CANCELED

                # search for a new placement

                # save application file into default path
                application_path = os.path.join(g.applications_path, application_obj.filename)
                shutil.copy(application_path, g.secfaas2fog_application_path)

                crashed_nodes = [node for node in list(crashed_node_id.values()) if node]

                is_successfully_replaced, replaced_application_chain = replace_application(
                    application_obj,
                    start_function,
                    starting_nodes,
                    crashed_nodes,
                    crashed_link,
                    infrastructure,
                    step_number
                )

                if is_successfully_replaced:
                    # update the application chain with the new placement
                    functions = replaced_application_chain.keys()
                    for function in functions:
                        for dependent_function in replaced_application_chain[function]:
                            if dependent_function not in application_obj.chain[function]:
                                application_obj.chain[function].append(dependent_function)

                else:
                    application_obj.state = ApplicationState.CANCELED

        # get nodes statistics
        for node in infrastructure.nodes.values():
            load = node.get_load()
            # in order to reduce the output report, don't save loads stat if load is 0
            if load > 0:
                node_data = {
                    'consumption' : node.get_energy(),
                    'load' : load,
                    'epoch' : step_number
                }
                node_stats[node.id].append(node_data)
        
        # update list of applications
        list_of_applications += apps_just_added

        # recalculate all paths between nodes of the physical infrastructure
        if type(infrastructure) is PhysicalInfrastructure:
            infrastructure.recalculate_routes()

        # update infastructure.pl
        dump_infrastructure(infrastructure, g.secfaas2fog_infrastructure_path)

        # make 1 step of simulation
        yield env.timeout(1)


# Entry point of the simulator
def main(argv):

    # INITIALIZATION PHASE - Global variables

    g.init()

    # logging
    logger = logs.init_logger()

    # configuration file path, set to default
    config_path = g.default_config_path

    # if the user use ask for help, print application usage message
    if ('-h' in argv or '--help' in argv):
        print_usage()
        return 0

    # we should have 0 or at most 2 command line arguments (-c config)
    if len(argv) not in [0, 2]:
        print_usage()
        return 1

    # parse command line arguments
    for i in range(0, len(argv) - 1, 2):
        
        option = argv[i]
        option_value = argv[i + 1]
        
        if (option == '-c'):
            # save into config_path variable
            config_path = option_value
        else:
            # unknown option
            logger.info("Unknown %s option", option)
    
    # check if the path is a file
    if not os.path.exists(config_path) or not os.path.isfile(config_path):
        logger.error("Config path '%s' not exists or is not a file" % config_path)
        logger.info("Fallback to default config file %s" % g.default_config_path)
        config_path = g.default_config_path
        # check that the default config exists
        if not os.path.exists(config_path) or not os.path.isfile(config_path):
            logger.critical("Default config path '%s' not exists or is not a file, exit..." % config_path)
            print_usage()
            return 1
    
    # parse the config file
    parsing_succeed = parse_config(config_path)

    if not parsing_succeed:
        logger.critical("Config parsing failed")
        print_usage()
        return 1
    else:
        logger.info("Config correctly parsed")
    
    # if silent mode is active don't show info messages but only errors and criticals
    if config.sim_silent_mode:
        logger.info("Silent mode is now active")
        logger.setLevel(logging.ERROR)
    
    # Seed for deterministic execution
    if config.sim_seed != -1:
        random.seed(config.sim_seed)
    
    # Instance infrastructure

    infrastructure : Infrastructure

    if config.infr_type == 'physical':
        logger.info("Infrastructure generation is starting")

        # randomly generate the infrastructure
        infrastructure = generate_infrastructure()

        # save infrastructure file into default path
        dump_infrastructure(infrastructure, g.secfaas2fog_infrastructure_path)

        logger.info(f"Infrastructure generated, it will be saved into the root directory")
        shutil.copy(g.secfaas2fog_infrastructure_path, g.generated_infrastructure_path)
    
    else:

        # load infrastructure from the Prolog file
        infrastructure = LogicalInfrastructure.loads(config.infr_filename)

        # save infrastructure file into default path
        shutil.copy(config.infr_filename, g.secfaas2fog_infrastructure_path)
    
    # initialize node stats dictionary
    for node in infrastructure.nodes.values():
        node_stats[node.id] = []

    # SIMPY PHASE
    
    # Instance an enviroment
    env = simpy.Environment()

    # start simulation
    env.process(simulation(env, config.sim_num_of_epochs, infrastructure))

    # we simulate for sim_num_of_epochs epochs
    env.run(until=config.sim_num_of_epochs)

    # STATISTICS

    logger.info("--- STATISTICS ---")

    global_number_of_placements = 0 # total number of placements (for all applications)
    global_successes = 0
    global_sum = 0

    applications_stats_keys = applications_stats.keys()

    for app_name in applications_stats_keys:

        application = applications_stats[app_name]
        
        # local accumulators
        num_of_placements = len(application['placements'])
        successes = 0
        sum = 0
        success_sum = 0
        failure_sum = 0

        placement_results = application['placements']
        
        for result in placement_results:
            
            end_millisec = result['end'].timestamp() * 1000
            start_millisec = result['start'].timestamp() * 1000
            exec_time = end_millisec - start_millisec
            sum += exec_time
            
            if result['success'] :
                success_sum += exec_time
                successes += 1
            else:
                failure_sum += exec_time
        
        # enrich application stats
        application['num_of_placements'] = num_of_placements
        application['successes'] = successes
        application['average_time_execution'] = 0 if num_of_placements == 0 else float(f'{sum/num_of_placements}')
        application['average_success_time_execution'] = 0 if successes == 0 else float(f'{success_sum/successes}')
        application['average_failure_time_execution'] = 0 if successes == num_of_placements else float(f'{failure_sum/(num_of_placements-successes)}')

        # accumulate global variables
        global_number_of_placements += num_of_placements
        global_successes += successes
        global_sum += sum
    
    stats_to_dump = {
        'total_placements' : global_number_of_placements,
        'total_successes' : global_successes,
        'average_secfaas2fog_execution' : 0 if global_number_of_placements == 0 else float(f'{global_sum/global_number_of_placements}'),
        'nodes' : {
            'load' : node_stats,
            'events' : node_events,
        },
        'links' : {
            'events' : link_events,
        },
        'applications' : applications_stats
    }

    logger.info("Number of placements: %d" % global_number_of_placements)
    logger.info("Successess: %d" % global_successes)

    logger.info("Writing JSON's execution report on '%s'", config.sim_report_output_file)

    with open(config.sim_report_output_file, 'w') as file:
        json.dump(stats_to_dump, indent = 4, default = str, fp = file)

    logger.info("Work done! Byee :)")

    return 0


if __name__ == "__main__":
    main(sys.argv[1:])
