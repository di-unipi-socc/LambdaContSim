import sys
from datetime import datetime
from swiplserver import PrologError, PrologMQI
import json
from application.application import Application, ApplicationState
from application.placed_function import FunctionState
from config import parse_config
from generate_infrastructure import generate_infrastructure
from infrastructure.infrastructure import Infrastructure
from infrastructure.node import NodeCategory
import os
import shutil
import config
from orchestration.orchestrator import Orchestrator
import logs
import logging
from placement import build_app_chain, parse_placement
import simpy
import global_variables as g
from utils import take_decision


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
        for event in event_gen.events:
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
    
    # write latencies informations
    graph_edges = infrastructure.graph.edges(data=True)
    for (node1, node2, edge_data) in graph_edges:
        
        # don't write a link with a crashed node
        if node1 in crashed_nodes:
            continue
        
        # don't write a link with a crashed node
        if node2 in crashed_nodes:
            continue
        
        latency = infrastructure.latencies[node1][node2]
        available = edge_data['available']
        # write iff link is available
        if available:
            string = f'latency({node1}, {node2}, {latency}).'
            lines.append(string)

    # overwrite file
    with open(output_filename, 'w') as f:
        for line in lines:
            f.write(line+'\n')


def place_application(
    application_name : str,
    application_filename : str,
    event : str,
    infrastructure : Infrastructure,
    applications_stats : dict,
    ):

    # get the logger
    logger = logs.get_logger()

    # try to place this app with SecFaas2Fog

    # it will reply with a valid placement iff application can be placed
    raw_placement = None
    application_can_be_placed = False
    query = False

    with PrologMQI(prolog_path_args=[
            "-s", g.secfaas2fog_placer_path
    ]) as mqi:
        with mqi.create_thread() as prolog_thread:

            try:

                # save SecFaas2Fog starting time
                start_time = datetime.now()
            
                query = prolog_thread.query(g.secfaas2fog_command)
            
            except PrologError:
                logger.error("Prolog execution failed")
            
            finally:
                # save SecFaas2Fog finish time
                end_time = datetime.now()

    if query != False and isinstance(query, list):
                    
        raw_placement = query[0] # it is a dictionary

        application_chain = build_app_chain(raw_placement)
        placement = parse_placement(raw_placement)
        
        #print(placement)
        #print(application_chain)

        application_can_be_placed = True

        logger.info("Placement found for %s", application_name)
    else:
        logger.info("Placement failed for %s", application_name)

    if application_name not in applications_stats.keys():
        applications_stats[application_name] = {}
        applications_stats[application_name]['placements'] = []

    # normal placement
    placement_data : dict = {
        'event' : event,
        'start' : start_time,
        'end' : end_time,
        'success' : application_can_be_placed
    }

    applications_stats[application_name]['placements'].append(placement_data)

    if application_can_be_placed :

        # create application instance
        application_obj = Application(application_name, application_filename, application_chain, placement, infrastructure.nodes)
        
        # place application over the infrastructure (update nodes capabilities: memory, number of vCPUs )
        functions = placement.keys()
        for function in functions:
            node_id = placement[function].node_id
            node_obj = infrastructure.nodes[node_id]
            
            # take resources from the node
            node_obj.take_resources(memory = placement[function].memory, v_cpu = placement[function].v_cpu)
        
        return application_obj
    
    return None


def simulation(
    env : simpy.Environment,
    steps : int,
    infrastructure : Infrastructure,
    applications_stats : dict,
    node_events : list,
    link_events : list
    ):
    
    # get logger
    logger = logs.get_logger()

    # list of applications
    list_of_applications : list[Application] = []

    for step_number in range(0, steps):
        
        # print the step
        logger.info("--- STEP %d ---", step_number)

        # PLACEMENT PHASE

        # we can place an application iff there is almost one active node
        if len(infrastructure.nodes) > len(infrastructure.crashed_nodes):

            # for each application
            for application_name in config.applications:

                app = config.applications[application_name]
                
                # we want to trigger a new placement request?
                trigger = take_decision(app['placement_trigger_probability'])
                
                # get application path
                application_filename = app['filename']
                application_path = os.path.join(g.applications_path, application_filename)

                if trigger:
                    logger.info("Placement triggered for application %s", application_name)

                    # save application file into default path
                    shutil.copy(application_path, g.secfaas2fog_application_path)

                    # place
                    event = "trigger"
                    application = place_application(application_name, application_filename, event, infrastructure, applications_stats)

                    if application is not None:
                        # launch application
                        thread = Orchestrator(env, application)
                        thread.start()

                        # add application into a list
                        list_of_applications.append(application)

                # update infastructure.pl
                dump_infrastructure(infrastructure, g.secfaas2fog_infrastructure_path)

        # CRASH/RESURRECTION PHASE

        # reset variables
        crashed_node_id = {}
        resurrected_node_id = {}
        first_node = None
        second_node = None
        
        # TODO commenta
        apps_just_added : list[Application] = []

        # NODE crash
        for category in ['cloud', 'fog', 'edge']:
            
            node_crashed = take_decision(config.crash_probability[category])

            node_resurrected = take_decision(config.resurrection_probability[category])

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

        # there are affected applications?
        for application in list_of_applications:

            # completed apps are not interesting
            if application.state == ApplicationState.COMPLETED:
                continue

            needs_new_placement = False
            
            # check if in the crashed node were deployed a function of this app
            # check only waiting and running functions
            for function_name in application.placement:
                function = application.placement[function_name]
                if function.state in [FunctionState.WAITING, FunctionState.RUNNING]:
                    if function.node_id in crashed_nodes:
                        
                        # app need a new placement
                        needs_new_placement = True
                        break
        
            if needs_new_placement:
                logger.info("Application %s needs a new placement", application.id)
                
                # update application status
                application.state = ApplicationState.CANCELED

                # trigger application functions
                for function_process in application.function_processes:
                    if function_process.fun.state == FunctionState.RUNNING:
                        function_process.action.interrupt()

                # release all resources of waiting functions
                for function_name in application.placement:
                    function = application.placement[function_name]
                    if function.state == FunctionState.WAITING:
                        node_id = function.node_id
                        node_obj = application.infrastructure_nodes[node_id]
                        node_obj.release_resources(function.memory, function.v_cpu)

                        logger.info("Application %s - Function %s has been canceled", application.id, function.id)
                        function_process.fun.state = FunctionState.CANCELED

                # search for a new placement

                # save application file into default path
                application_path = os.path.join(g.applications_path, application.filename)
                shutil.copy(application_path, g.secfaas2fog_application_path)

                # TODO sistema print
                event = f"node(s) {[node for node in list(crashed_node_id.values())]} crashed"

                application = place_application(application.id, application.filename, event, infrastructure, applications_stats)

                if application is not None:
                    # launch application
                    thread = Orchestrator(env, application)
                    thread.start()

                    # add application into a list
                    # this application must not be affected by the crash because
                    # it has been just placed
                    # so we add it in a temportary app list
                    apps_just_added.append(application)                                           

        # LINK crash
        link_crashed = take_decision(config.link_crash_probability)

        link_resurrected = take_decision(config.link_resurrection_probability)

        if link_crashed:
            first_node, second_node = infrastructure.simulate_link_crash()
            
            if first_node != None and second_node != None:
                logger.info("Link %s <-> %s crashed", first_node, second_node)

                # add event to the list
                event = {
                    'type' : 'crash',
                    'first_node_id' : first_node,
                    'second_node_id' : second_node,
                    'epoch' : step_number
                }
                link_events.append(event)

                # a link crash affect the app iff the 2 nodes were 'consecutive'
                # functions must be waiting or running
                # there are affected applications?
                for application in list_of_applications:

                    # completed apps are not interesting
                    if application.state == ApplicationState.COMPLETED:
                        continue

                    needs_new_placement = False
                    
                    # check if in the crashed node were deployed a function of this app
                    # check only waiting and running functions
                    for function_name in application.placement:
                        function = application.placement[function_name]
                        if function.state in [FunctionState.WAITING, FunctionState.RUNNING]:
                            # TODO make it better
                            if function.node_id in [first_node, second_node]:
                                needs_new_placement = True
                                break
                
                    if needs_new_placement:
                        logger.info("Application %s needs a new placement", application.id)
                        
                        # update application status
                        application.state = ApplicationState.CANCELED

                        # trigger application functions
                        for function_process in application.function_processes:
                            if function_process.fun.state == FunctionState.RUNNING:
                                function_process.action.interrupt()

                        # release all resources of waiting functions
                        for function_name in application.placement:
                            function = application.placement[function_name]
                            if function.state == FunctionState.WAITING:
                                node_id = function.node_id
                                node_obj = application.infrastructure_nodes[node_id]
                                node_obj.release_resources(function.memory, function.v_cpu)

                                logger.info("Application %s - Function %s has been canceled", application.id, function.id)
                                function_process.fun.state = FunctionState.CANCELED

                        # search for a new placement

                        # save application file into default path
                        application_path = os.path.join(g.applications_path, application.filename)
                        shutil.copy(application_path, g.secfaas2fog_application_path)

                        event = "link %s <-> %s crashed" % (first_node, second_node)

                        application = place_application(application.id, application.filename, event, infrastructure, applications_stats)

                        if application is not None:
                            thread = Orchestrator(env, application)
                            thread.start()

                            # add application into a list
                            # this application must not be affected by the crash because
                            # it has been just placed
                            # so we add it in a temportary app list
                            apps_just_added.append(application)                                           
     
        if link_resurrected:

            if first_node is not None and second_node is not None:
                link_to_exclude = {'first' : first_node, 'second' : second_node}
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
        
        # update list of applications
        list_of_applications += apps_just_added

        # update infrastructure
        infrastructure.update()

        # update infastructure.pl
        dump_infrastructure(infrastructure, g.secfaas2fog_infrastructure_path)

        # make 1 step
        yield env.timeout(1)


# Entry point of the simulator
def main(argv):

    # INITIALIZATION PHASE - Global variables

    g.init()

    # logging
    logger = logs.init_logger()

    # statistical variables
    applications_stats : dict = {}
    node_events : list = []
    link_events : list = []

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
    config_has_parsed = parse_config(config_path)

    if not config_has_parsed:
        logger.critical("Config parsing failed") # TODO devo stamparlo qui?
        print_usage()
        return 1
    else:
        logger.info("Config correctly parsed")
    
    # If silent mode is active don't show info messages but only errors and criticals
    if(config.silent_mode):
        logger.info("Silent mode is now active")
        logger.setLevel(logging.ERROR)

    # instance infrastructure
    infrastructure : Infrastructure = generate_infrastructure()

    # save infrastructure file into default path
    dump_infrastructure(infrastructure, g.secfaas2fog_infrastructure_path)

    # SIMPY PHASE
    
    # Instance an enviroment
    env = simpy.Environment()

    # start simulation
    env.process(simulation(env, config.num_of_epochs, infrastructure, applications_stats, node_events, link_events))

    # we simulate for num_of_epochs epochs
    env.run(until=config.num_of_epochs)

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

        placement_results = application['placements']
        
        for result in placement_results:
            
            end_millisec = result['end'].timestamp() * 1000
            start_millisec = result['start'].timestamp() * 1000
            sum += end_millisec - start_millisec
            
            if result['success'] :
                successes += 1
        
        # enrich application stats
        application['num_of_placements'] = num_of_placements
        application['successes'] = successes
        application['average_secfaas2fog_execution'] = float(f'{sum/num_of_placements}')

        # accumulate global variables
        global_number_of_placements += num_of_placements
        global_successes += successes
        global_sum += sum
    
    stats_to_dump = {
        'total_placements' : global_number_of_placements,
        'total_successes' : global_successes,
        'average_secfaas2fog_execution' : float(f'{global_sum/global_number_of_placements}'),
        'node_events' : node_events,
        'link_events' : link_events,
        'data' : applications_stats
    }

    logger.info("Number of placements: %d" % global_number_of_placements)
    logger.info("Average time of SecFaas2Fog placement: " + str(float(f'{global_sum/global_number_of_placements:.2f}')) + " milliseconds")
    logger.info("Successess: %d" % global_successes)

    logger.info("Writing JSON's execution report on '%s'", config.report_output_file)

    with open(config.report_output_file, 'w') as file:
        json.dump(stats_to_dump, indent = 4, default = str, fp = file)

    logger.info("Work done! Byee :)")

    return 0


if __name__ == "__main__":
    main(sys.argv[1:])
