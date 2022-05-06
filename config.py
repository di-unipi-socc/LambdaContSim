import yaml
import os
import global_variables as g

def parse_config(path):
    
    # app global variables
    global report_output_file
    global silent_mode
    global num_of_epochs
    global function_duration
    global infrastructure_temp_path
    global node_crash_probability
    global node_resurrection_probability
    global link_crash_probability
    global link_resurrection_probability
    global applications

    with open(path, 'r') as f:
        
        # load config yaml file into a dictionary
        config = yaml.load(f, Loader=yaml.FullLoader)

        report_output_file = config['output_file']
        silent_mode = config['silent_mode']
        num_of_epochs = config['epochs']
        function_duration = config['function_duration'] # TODO default 1
        
        infrastructure_filename = config['infrastructure_filename']
        infrastructure_temp_path = os.path.join(g.infrastructures_path, infrastructure_filename)

        node_crash_probability = config['node_crash_probability']
        node_resurrection_probability = config['node_resurrection_probability']
        link_crash_probability = config['link_crash_probability']
        link_resurrection_probability = config['link_resurrection_probability']
        
        
        if not os.path.isfile(infrastructure_temp_path):
            return False
        
        applications = config['applications']

        # check that paths are correct
        for app in applications:
            application_filename = app['filename']
            application_path = os.path.join(g.applications_path, application_filename)
            if not os.path.isfile(application_path):
                # TODO log?
                return False

        # TODO check values

        # TODO PRINT VALUES TO SHOW SUCCESS?
        
        return True
