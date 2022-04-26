# ==============================================================================
#
#       global_variables.py - Global variables shared by all modules.
#
# ==============================================================================

secfaas2fog_abs_path = ""
default_placer_path = ""
default_application_path = ""
default_infrastructure_path = ""
default_config_path = ""
secfaas2fog_command = ""

def init():
    """ This should only be called once by the main module
        Child modules will inherit values. For example if they contain
        
            import global_variables as g
            
        Later on they can reference 'g.logger' to get the logger
    """

    global secfaas2fog_abs_path
    global default_placer_path
    global default_application_path
    global default_infrastructure_path
    global default_config_path
    global secfaas2fog_command

    # define where SecFaas2Fog is
    import os
    secfaas2fog_folder = os.path.join(os.curdir,'SecFaas2Fog')
    secfaas2fog_abs_path = os.path.abspath(
        os.path.expanduser(os.path.expandvars(secfaas2fog_folder)))

    # default Prolog files path
    default_placer_path = os.path.join(secfaas2fog_abs_path,'placer.pl')
    default_application_path = os.path.join(secfaas2fog_abs_path, 'application.pl')
    default_infrastructure_path = os.path.join(secfaas2fog_abs_path, 'infrastructure.pl')

    # default config path
    default_config_path = os.path.join(os.curdir,'config.yaml')

    # SecFaas2Fog Prolog command
    # once means that we take the first of the results
    secfaas2fog_command = "once(secfaas2fog(OrchestrationId, Placement))."