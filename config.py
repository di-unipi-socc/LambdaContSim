import yaml
import os
import global_variables as g
import logs
from datetime import datetime

def parse_config(path):
    
    # config variables

    # SIMULATOR
    global sim_report_output_file
    global sim_silent_mode
    global sim_num_of_epochs
    global sim_function_duration
    global sim_seed
    global sim_use_padding
    global sim_max_placement_time

    # EVENTS
    global event_generator_trigger_probability
    global event_min_probability
    global event_max_probability

    # INFRASTRUCTURE
    global infr_type
    global infr_filename
    global infr_is_dynamic
    global infr_node_crash_probability
    global infr_node_resurrection_probability
    global infr_link_crash_probability
    global infr_link_resurrection_probability
    global infr_energy
    
    # APPLICATIONS
    global applications

    # get logger

    logger = logs.get_logger()

    with open(path, 'r') as f:
        
        # load config yaml file into a dictionary
        config = yaml.load(f, Loader=yaml.FullLoader)

        # SIMULATOR

        sim_silent_mode = bool(config['simulator']['silent_mode'])
        sim_num_of_epochs = int(config['simulator']['epochs'])
        sim_function_duration = int(config['simulator']['function_duration'])

        sim_seed = int(config['simulator']['seed'])
        sim_use_padding = bool(config['simulator']['use_padding'])
        sim_max_placement_time = int(config['simulator']['max_placement_time'])

        temp_file_prefix = str(config['simulator']['output_file_prefix'])
        
        # file prefix is 'report' if the used doesn't write it
        file_prefix = 'report' if temp_file_prefix == '' else temp_file_prefix
        datetime_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file_basename = file_prefix + " " + datetime_str + ".json"
        report_folder_path = os.path.join(os.getcwd(), 'reports')
        file_path = os.path.join(report_folder_path, file_basename)

        # create report folder if it doesn't exist
        os.makedirs(report_folder_path, exist_ok = True)

        sim_report_output_file = file_path

        # SIMULATOR CHECKS
        
        if sim_num_of_epochs < 1:
            logger.error("Number of epochs must be greater or equal 1")
            return False
        
        if sim_function_duration < 1:
            logger.error("Function duration must be greater or equal 1")
            return False
        
        if sim_seed < -1:
            logger.error("Simulator seed must be -1 (ignore seed) or greater or equal 0")
            return False
        
        if sim_max_placement_time < 1:
            logger.error("Max placement time must be greater or equal 1 (seconds)")
            return False

        # EVENTS

        event_generator_trigger_probability = float(config['events']['generator_trigger_probability'])
        event_min_probability = float(config['events']['event_min_probability'])
        event_max_probability = float(config['events']['event_max_probability'])

        # EVENTS CHECK

        if event_generator_trigger_probability > 1 or event_generator_trigger_probability < 0:
            logger.error("Probability of trigger generator must be a value between 0 and 1")
            return False
        
        if event_min_probability > 1 or event_min_probability < 0:
            logger.error("Minimum probability of event trigger must be a value between 0 and 1")
            return False
        
        if event_max_probability > 1 or event_max_probability < 0:
            logger.error("Minimum probability of event trigger must be a value between 0 and 1")
            return False
        
        if event_min_probability > event_max_probability:
            logger.error("Minimum probability of event trigger can't be greater than maximum probability")
            return False

        # INFRASTRUCTURE

        infr_type = str(config['infrastructure']['type'])
        if not infr_type in ['physical', 'logical']:
            logger.error("Only allowed value for infrastructure type are 'physical' and 'logical'")
            return False
        
        # if the infrastructur is logical, we need to take it from a Prolog file
        if infr_type == 'logical':
            infr_temp_filename = str(config['infrastructure']['filename'])
            infr_filename = os.path.join(g.infrastructures_path, infr_temp_filename)

            if not os.path.isfile(infr_filename):
                logger.error("If infrastructure type is 'logical', a valid infrastructure file must be given")
                return False
        else:
            infr_filename = ''
        
        infr_is_dynamic = bool(config['infrastructure']['is_dynamic'])

        if infr_is_dynamic:

            # Node crash and resurrection probabilities

            infr_node_crash_probability = dict(config['infrastructure']['crash_probability'])
            infr_node_resurrection_probability = dict(config['infrastructure']['resurrection_probability'])

            for key in ['cloud', 'fog', 'edge']:
                if key not in infr_node_crash_probability:
                    logger.error(f'{key} is missing from infrastructure node crash probability')
                    return False
                if key not in infr_node_crash_probability:
                    logger.error(f'{key} is missing from infrastructure node resurrection probability')
                    return False

            # Link crash and resurrection probabilities

            infr_link_crash_probability = float(config['infrastructure']['link_crash_probability'])
            infr_link_resurrection_probability = float(config['infrastructure']['link_resurrection_probability'])
        else:

            # infrastructure is static -> no crashes or resurrections

            infr_node_crash_probability = {
                'edge' : 0,
                'fog' : 0,
                'cloud' : 0
            }
            infr_node_resurrection_probability = {
                'edge' : 0,
                'fog' : 0,
                'cloud' : 0
            }
            infr_link_crash_probability = 0
            infr_link_resurrection_probability = 0
        
        infr_energy = dict(config['infrastructure']['energy'])

        # APPLICATIONS
        
        applications = dict(config['applications'])

        # APPLICATIONS CHECKS
        
        for app_name in applications:
            app = applications[app_name]
            application_filename = app['filename']
            application_path = os.path.join(g.applications_path, application_filename)
            if not os.path.isfile(application_path):
                logger.error(f'{app_name} application path is not a file')
                return False
        
        return True
