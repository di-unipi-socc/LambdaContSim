import re
import sys, random
from datetime import datetime
from swiplserver import PrologError, PrologMQI
import json
from config import parse_config
from infrastructure.infrastructure import Infrastructure
from infrastructure.node import Node
from application.function import PlacedFunction
from math import inf
import os
import shutil
import config
from orchestration.orchestrator import Orchestrator
import logs
import logging
from placement import build_app_chain, parse_placement


def print_usage():
    ''' Print application usage message'''
    print('Usage: %s [<options>]' % os.path.basename(sys.argv[0]))
    print('       %s [-h|--help] to show this help message' % os.path.basename(sys.argv[0]))
    print('\nOptions:')
    print('-c <config file> application config (default config.yaml)')


def take_decision(probability : float) -> bool:

    return random.random() < probability

# TODO commenta
def load_infrastructure(infrastructure_filename : str) -> Infrastructure:
    
    nodes : dict[str, Node] = {}
    latencies : dict[str, dict[str, ( int, bool )]] = {}
    
    # TODO check errors on file opening
    node_pattern = r'^node\(([^,]+),([^,]+),(\[.*?\]),(\[.*?\]),\(([^,]+),([^,]+),([^\)]+)\)\)\.*'
    latency_pattern = r'^latency\(([^,]+),([^,]+),([^,]+)\)\.*'

    other_lines = []

    with open(infrastructure_filename, 'r') as f:
        lines = f.readlines()

        for line in lines:
            if line.startswith('node'):
                line = line.replace(' ', '')
                # print(line)
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
        # instance infrastructure
        infrastructure = Infrastructure(nodes, latencies, other_lines)

        return infrastructure


# TODO commenta
def dump_infrastructure(infrastructure : Infrastructure, output_filename: str):
    lines = []

    nodes = infrastructure.nodes

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
    with open(output_filename, 'w') as f:
        for line in lines:
            f.write(line)

# Entry point of the simulator
def main(argv):

    # Setting up

    # logging
    logger = logs.init_logger() # TODO make it global??

    # define where SecFaas2Fog is
    secfaas2fog_folder = os.path.join(os.curdir,'SecFaas2Fog')
    secfaas2fog_abs_path = os.path.abspath(
        os.path.expanduser(os.path.expandvars(secfaas2fog_folder)))

    # define defaults Prolog files path
    default_placer_path = os.path.join(secfaas2fog_abs_path,'placer.pl')
    default_application_path = os.path.join(secfaas2fog_abs_path, 'application.pl')
    default_infrastructure_path = os.path.join(secfaas2fog_abs_path, 'infrastructure.pl')

    # define default config path
    default_config_path = os.path.join(os.curdir,'config.yaml')

    # statistical variables
    applications_stats : dict = {}
    node_events : list = []
    link_events : list = []

    # configuration file path, set to default
    config_path = default_config_path

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
        logger.info("Fallback to default config file %s" % default_config_path)
        config_path = default_config_path
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
    
    # get from config list of applications
    applications = config.applications

    # save infrastructure file into default path
    shutil.copy(config.infrastructure_temp_path, default_infrastructure_path)

    # instance infrastructure
    infrastructure : Infrastructure = load_infrastructure(default_infrastructure_path)
    
    # declare Prolog variable
    # once means that we take the first of the results
    secfaas2fog_command = "once(secfaas2fog(OrchestrationId, Placement))."

    for index in range(0, config.num_of_epochs):

        # PLACEMENT PHASE

        # we can place an application iff there is almost one active node
        if len(infrastructure.nodes) > len(infrastructure.crashed_nodes):

            # for each application
            for app in applications:
                
                # we want to trigger a new placement request?
                trigger = take_decision(app['placement_trigger_probability'])
                application_path = app['path']

                # get the name of the application (file)
                application_name = os.path.basename(application_path)

                if trigger:
                    logger.info("Placement triggered for application %s", application_name)

                    # save application file into default path
                    shutil.copy(application_path, default_application_path)

                    # try to place this app with SecFaas2Fog

                    # it will reply with a valid placement iff application can be placed
                    raw_placement = None
                    application_can_be_placed = False
                    query = False
                    
                    # save SecFaas2Fog starting time
                    start_time = datetime.now()
                    
                    with PrologMQI(prolog_path_args=[
                            "-s", default_placer_path
                    ]) as mqi:
                        with mqi.create_thread() as prolog_thread:

                            try:
                            
                                query = prolog_thread.query(secfaas2fog_command)
                            
                            except PrologError:
                                logger.error("Prolog execution failed")
                            
                            finally:
                                # save SecFaas2Fog finish time
                                end_time = datetime.now()

                    if query != False and isinstance(query, list):
                                    
                        raw_placement = query[0] # it is a dictionary

                        function_chain = build_app_chain(raw_placement)
                        placement = parse_placement(raw_placement)
                        
                        #print(placement)
                        #print(function_chain)

                        application_can_be_placed = True

                        logger.info("Placement found for %s", application_name)
                    else:
                        logger.info("Placement failed for %s", application_name)
                    
                    if application_name not in applications_stats.keys():
                        applications_stats[application_name] = {}
                        applications_stats[application_name]['placements'] = []

                    # normal placement
                    placement_data : dict = {
                        'event' : "trigger",
                        'start' : start_time,
                        'end' : end_time,
                        'success' : application_can_be_placed
                    }

                    applications_stats[application_name]['placements'].append(placement_data)

                    if (application_can_be_placed) :

                        # create application instance
                        # TODO actually we have 1 application so it is defined above

                        # place application over the infrastructure (update nodes capabilities: memory, number of vCPUs )
                        functions = placement.keys()
                        for function in functions:
                            node_id = placement[function].node_id
                            node_obj = infrastructure.nodes[node_id]
                            
                            # take resources from the node
                            node_obj.take_resources(memory = placement[function].memory, v_cpu = placement[function].v_cpu)

                        # launch application
                        thread = Orchestrator("Placement", 1000 + index, infrastructure.nodes, function_chain, placement)
                        thread.start()

                # update infastructure.pl
                dump_infrastructure(infrastructure, default_infrastructure_path)

        # CRASH/RESURRECTION PHASE

        # node crash
        node_crashed = take_decision(config.node_crash_probability)

        node_resurrected = take_decision(config.node_resurrection_probability)

        # link crash
        link_crashed = take_decision(config.link_crash_probability)

        link_resurrected = take_decision(config.link_resurrection_probability)

        if node_crashed:
            node_id = infrastructure.simulate_node_crash()
            if node_id is not None:
                logger.info("Node %s crashed", node_id)
                
                # add event to the list
                event = {
                    'type' : 'crash',
                    'node_id' : node_id,
                    'when' : datetime.now()
                }
                node_events.append(event)

                # TODO there are affected applications?
        
        elif node_resurrected:
            node_id = infrastructure.simulate_node_resurrection()
            if node_id is not None:
                logger.info("Node %s resurrected", node_id)

                # add event to the list
                event = {
                    'type' : 'resurrection',
                    'node_id' : node_id,
                    'when' : datetime.now()
                }
                node_events.append(event)
        
        if link_crashed:
            first_node, second_node = infrastructure.simulate_link_crash()
            if first_node != None and second_node != None:
                logger.info("Link %s <-> %s crashed", first_node, second_node)

                # add event to the list
                event = {
                    'type' : 'crash',
                    'first_node_id' : first_node,
                    'second_node_id' : second_node,
                    'when' : datetime.now()
                }
                link_events.append(event)

                # TODO there are affected applications?
        
        elif link_resurrected:
            first_node, second_node = infrastructure.simulate_link_resurrection()
            if first_node != None and second_node != None:
                logger.info("Link %s <-> %s resurrected", first_node, second_node)

                # add event to the list
                event = {
                    'type' : 'resurrection',
                    'first_node_id' : first_node,
                    'second_node_id' : second_node,
                    'when' : datetime.now()
                }
                link_events.append(event)
        
        # update infastructure.pl
        dump_infrastructure(infrastructure, default_infrastructure_path)

    # statistical prints

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
