import yaml
import os
import global_variables as g

def parse_config(path):
    
    # config variables

    # SIMULATOR
    global sim_report_output_file
    global sim_silent_mode
    global sim_num_of_epochs
    global sim_function_duration
    global sim_seed

    # INFRASTRUCTURE
    global infr_type
    global infr_filename
    global infr_is_dynamic
    global infr_node_crash_probability
    global infr_node_resurrection_probability
    global infr_link_crash_probability
    global infr_link_resurrection_probability
    
    # APPLICATIONS
    global applications

    with open(path, 'r') as f:
        
        # load config yaml file into a dictionary
        config = yaml.load(f, Loader=yaml.FullLoader)

        # SIMULATOR

        sim_report_output_file = config['simulator']['output_file']
        sim_silent_mode = config['simulator']['silent_mode']
        sim_num_of_epochs = config['simulator']['epochs']
        sim_function_duration = config['simulator']['function_duration']

        # check function duration
        if sim_function_duration < 1:
            sim_function_duration = 1

        sim_seed = config['simulator']['seed']

        # INFRASTRUCTURE

        infr_type = config['infrastructure']['type']
        if not infr_type in ['physical', 'logical']:
            # TODO error message
            return False
        
        # if the infrastructur is logical, we need to take it from a Prolog file
        if infr_type == 'logical':
            infr_temp_filename = config['infrastructure']['filename']
            infr_filename = os.path.join(g.infrastructures_path, infr_temp_filename)
        else:
            infr_filename = ''
        
        infr_is_dynamic = config['infrastructure']['is_dynamic']

        if infr_is_dynamic:

            # Node crash and resurrection probabilities

            infr_node_crash_probability = config['infrastructure']['crash_probability']
            infr_node_resurrection_probability = config['infrastructure']['resurrection_probability']

            # Link crash and resurrection probabilities

            infr_link_crash_probability = config['infrastructure']['link_crash_probability']
            infr_link_resurrection_probability = config['infrastructure']['link_resurrection_probability']
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

        # APPLICATIONS
        
        applications = config['applications']

        # check that paths are correct
        for app_name in applications:
            app = applications[app_name]
            application_filename = app['filename']
            application_path = os.path.join(g.applications_path, application_filename)
            if not os.path.isfile(application_path):
                # TODO log?
                return False

        # TODO check values
        
        return True
