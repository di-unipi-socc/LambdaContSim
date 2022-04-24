import yaml
import os

def parse_config(path):
    
    # variabili globali nell'applicazione
    global num_of_epochs
    global infrastructure_temp_path
    global node_crash_probability
    global link_crash_probability
    global applications

    with open(path, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

        #print(config)

        num_of_epochs = config['epochs']
        infrastructure_temp_path = config['infrastructure_path']
        node_crash_probability = config['node_crash_probability']
        link_crash_probability = config['link_crash_probability']
        
        
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
