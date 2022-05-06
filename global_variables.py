# ==============================================================================
#
#       global_variables.py - Global variables shared by all modules.
#
# ==============================================================================

secfaas2fog_path = ""
secfaas2fog_placer_path = ""
secfaas2fog_application_path = ""
secfaas2fog_infrastructure_path = ""
infrastructures_path = ""
applications_path = ""
default_config_path = ""
secfaas2fog_command = ""

def init():
    """ This should only be called once by the main module
        Child modules will inherit values. For example if they contain
        
            import global_variables as g
            
        Later on they can reference 'g.logger' to get the logger
    """

    global secfaas2fog_path
    global secfaas2fog_placer_path
    global secfaas2fog_application_path
    global secfaas2fog_infrastructure_path
    global infrastructures_path
    global applications_path
    global default_config_path
    global secfaas2fog_command

    # define where SecFaas2Fog is
    import os
    secfaas2fog_path = os.path.join(os.curdir, 'SecFaas2Fog')

    # default Prolog files path
    secfaas2fog_placer_path = os.path.join(secfaas2fog_path, 'placer.pl')
    secfaas2fog_application_path = os.path.join(secfaas2fog_path, 'application.pl')
    secfaas2fog_infrastructure_path = os.path.join(secfaas2fog_path, 'infrastructure.pl')

    # default infrastructures and applications paths
    infrastructures_path = os.path.join(os.curdir, 'test_set', 'infrastructures')
    applications_path = os.path.join(os.curdir, 'test_set', 'applications')

    # default config path
    default_config_path = os.path.join(os.curdir, 'config.yaml')

    # SecFaas2Fog Prolog command
    # once means that we take the first of the results
    secfaas2fog_command = "once(secfaas2fog(OrchestrationId, Placement))."