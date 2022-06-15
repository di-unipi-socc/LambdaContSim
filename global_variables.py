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
generated_infrastructure_path = ""


def init():
    """This should only be called once by the main module
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
    global generated_infrastructure_path

    # define where SecFaaS2Fog is
    import os

    secfaas2fog_path = os.path.join(os.curdir, "SecFaaS2Fog")

    # default Prolog files path
    secfaas2fog_placer_path = os.path.join(secfaas2fog_path, "placer.pl")
    secfaas2fog_application_path = os.path.join(secfaas2fog_path, "application.pl")
    secfaas2fog_infrastructure_path = os.path.join(
        secfaas2fog_path, "infrastructure.pl"
    )

    # default infrastructures and applications paths
    infrastructures_path = os.path.join(os.curdir, "test_set", "infrastructures")
    applications_path = os.path.join(os.curdir, "test_set", "applications")

    # default config path
    default_config_path = os.path.join(os.curdir, "config.yaml")

    # where we save the generated infrastructure file
    generated_infrastructure_path = os.path.join(
        os.curdir, "generated_infrastructure.pl"
    )
