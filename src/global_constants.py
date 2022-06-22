# ==============================================================================
#
#       global_constants.py - Global variables shared by all modules.
#
# ==============================================================================

ROOT_DIR = ""
SECF2F_PLACER_PATH = ""
SECF2F_APP_PATH = ""
SECF2F_INFRASTRUCTURE_PATH = ""
INFRASTRUCTURES_DIR = ""
APPLICATIONS_DIR = ""
DEFAULT_CONFIG_PATH = ""
DEFAULT_INFRASTRUCTURE_CONFIG_PATH = ""
GENERATED_INFRASTRUCTURE_PATH = ""
REPORT_DIR = ""


def init():
    """
    This should only be called once by the main module
    Child modules will inherit values
    """

    global ROOT_DIR
    global SECF2F_PLACER_PATH
    global SECF2F_APP_PATH
    global SECF2F_INFRASTRUCTURE_PATH
    global INFRASTRUCTURES_DIR
    global APPLICATIONS_DIR
    global DEFAULT_CONFIG_PATH
    global DEFAULT_INFRASTRUCTURE_CONFIG_PATH
    global GENERATED_INFRASTRUCTURE_PATH
    global REPORT_DIR

    import os

    # project root dir
    ROOT_DIR = os.path.dirname(os.path.abspath(os.path.join(__file__, os.pardir)))

    # define where SecFaaS2Fog is
    secfaas2fog_path = os.path.join(ROOT_DIR, "SecFaaS2Fog")

    # default Prolog files path
    SECF2F_PLACER_PATH = os.path.join(secfaas2fog_path, "placer.pl")
    SECF2F_APP_PATH = os.path.join(secfaas2fog_path, "application.pl")
    SECF2F_INFRASTRUCTURE_PATH = os.path.join(secfaas2fog_path, "infrastructure.pl")

    # default infrastructures and applications paths
    INFRASTRUCTURES_DIR = os.path.join(ROOT_DIR, "test_set", "infrastructures")
    APPLICATIONS_DIR = os.path.join(ROOT_DIR, "test_set", "applications")

    # default config path
    DEFAULT_CONFIG_PATH = os.path.join(ROOT_DIR, "config.yaml")

    # default infrastructure config path
    DEFAULT_INFRASTRUCTURE_CONFIG_PATH = os.path.join(
        ROOT_DIR, "infrastructure_config.yaml"
    )

    # where we save the generated infrastructure file
    GENERATED_INFRASTRUCTURE_PATH = os.path.join(
        ROOT_DIR, "generated_infrastructure.pl"
    )

    # where reports are stored
    REPORT_DIR = os.path.join(
        ROOT_DIR, "reports"
    )
