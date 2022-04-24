import yaml
import os

def parse_config(path):
    
    # variabili globali nell'applicazione
    global placement_trigger_probability
    global num_of_epochs
    global infrastructure_temp_path
    global node_crash_probability
    global link_crash_probability
    global applications

    with open(path, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

        #print(config)

        placement_trigger_probability = config['placement_trigger']
        num_of_epochs = config['epochs']
        infrastructure_temp_path = config['infrastructure_path']
        node_crash_probability = config['node_crash_probability']
        link_crash_probability = config['link_crash_probability']
        
        
        if not os.path.isfile(infrastructure_temp_path):
            return False
        
        applications = config['applications']

        # TODO check values

        # TODO PRINT VALUES TO SHOW SUCCESS?
        
        return True
