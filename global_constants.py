# ==============================================================================
#
#       global_constants.py - Global variables shared by all modules.
#
# ==============================================================================

SECF2F_PLACER_PATH = ""
SECF2F_APP_PATH = ""
SECF2F_INFRASTRUCTURE_PATH = ""
INFRASTRUCTURES_PATH = ""
APPLICATIONS_PATH = ""
DEFAULT_CONFIG_PATH = ""
DEFAULT_INFRASTRUCTURE_CONFIG_PATH = ""
GENERATED_INFRASTRUCTURE_PATH = ""


def init():
    """
    This should only be called once by the main module
    Child modules will inherit values
    """

    global SECF2F_PLACER_PATH
    global SECF2F_APP_PATH
    global SECF2F_INFRASTRUCTURE_PATH
    global INFRASTRUCTURES_PATH
    global APPLICATIONS_PATH
    global DEFAULT_CONFIG_PATH
    global DEFAULT_INFRASTRUCTURE_CONFIG_PATH
    global GENERATED_INFRASTRUCTURE_PATH

    # define where SecFaaS2Fog is
    import os

    secfaas2fog_path = os.path.join(os.curdir, "SecFaaS2Fog")

    # default Prolog files path
    SECF2F_PLACER_PATH = os.path.join(secfaas2fog_path, "placer.pl")
    SECF2F_APP_PATH = os.path.join(secfaas2fog_path, "application.pl")
    SECF2F_INFRASTRUCTURE_PATH = os.path.join(secfaas2fog_path, "infrastructure.pl")

    # default infrastructures and applications paths
    INFRASTRUCTURES_PATH = os.path.join(os.curdir, "test_set", "infrastructures")
    APPLICATIONS_PATH = os.path.join(os.curdir, "test_set", "applications")

    # default config path
    DEFAULT_CONFIG_PATH = os.path.join(os.curdir, "config.yaml")

    # default infrastructure config path
    DEFAULT_INFRASTRUCTURE_CONFIG_PATH = os.path.join(
        os.curdir, "infrastructure_config.yaml"
    )

    # where we save the generated infrastructure file
    GENERATED_INFRASTRUCTURE_PATH = os.path.join(
        os.curdir, "generated_infrastructure.pl"
    )
