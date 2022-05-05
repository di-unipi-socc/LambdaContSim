import yaml
import os

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
        infrastructure_temp_path = config['infrastructure_path']
        node_crash_probability = config['node_crash_probability']
        node_resurrection_probability = config['node_resurrection_probability']
        link_crash_probability = config['link_crash_probability']
        link_resurrection_probability = config['link_resurrection_probability']
        
        
        if not os.path.isfile(infrastructure_temp_path):
            return False
        
        applications = config['applications']

        # check that paths are correct
        for app in applications:
            if not os.path.isfile(app['path']):
                # TODO log?
                return False

        # TODO check values

        # TODO PRINT VALUES TO SHOW SUCCESS?
        
        return True
