import yaml
import os
import global_variables as g

def parse_config(path):
    
    # app global variables
    global report_output_file
    global silent_mode
    global num_of_epochs
    global function_duration
    global crash_probability
    global resurrection_probability
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

        # Node crash and resurrection probabilities

        crash_probability = config['crash_probability']
        resurrection_probability = config['resurrection_probability']

        # Link crash and resurrection probabilities

        link_crash_probability = config['link_crash_probability']
        link_resurrection_probability = config['link_resurrection_probability']
        
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
