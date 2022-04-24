import yaml
import os

def parse_config(path):
    
    # variabili globali nell'applicazione
    global placement_trigger_probability
    global num_of_epochs
    global infrastructure_temp_path
    global applications

    with open(path, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

        #print(config)

        placement_trigger_probability = config['placement_trigger']
        num_of_epochs = config['epochs']
        infrastructure_temp_path = config['infrastructure_path']
        
        
        if not os.path.isfile(infrastructure_temp_path):
            return False
        
        applications = []
        
        applications_list = config['applications']
        # applications
        for app in applications_list:
            if not os.path.isfile(app['path']):
                return False
            elem = {
                'path' : app['path'],
                'node_trigger' : app['node_trigger'],
                'link_trigger' : app['link_trigger']
            }
            applications.append(elem)
        
        return True
