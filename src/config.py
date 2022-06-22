import yaml
import os
import global_constants as gc
import logs
from datetime import datetime


def parse_config(path):
    """
    Parse simulator config file.
    Returns True iff config is correctly parsed
    """

    # config variables

    # SIMULATOR
    global sim_report_output_file
    global sim_num_of_epochs
    global sim_function_duration
    global sim_seed
    global sim_use_padding
    global sim_max_placement_time

    # EVENTS
    global event_generator_trigger_probability
    global event_min_probability
    global event_max_probability

    # INFRASTRUCTURE
    global infr_type
    global infr_is_dynamic
    global infr_node_crash_probability
    global infr_node_resurrection_probability
    global infr_link_crash_probability
    global infr_link_resurrection_probability
    global infr_energy

    # APPLICATIONS
    global applications

    # get logger

    logger = logs.get_logger()

    yml_config: dict = {}

    with open(path, "r") as config_file:

        # load config yaml file into a dictionary
        try:
            yml_config = yaml.load(config_file, Loader=yaml.FullLoader)

        except yaml.YAMLError:
            logger.critical("Error while parsing YAML file: invalid structure")
            return False

    # SIMULATOR

    sim_num_of_epochs = int(yml_config["simulator"]["epochs"])
    sim_function_duration = int(yml_config["simulator"]["function_duration"])

    sim_seed = int(yml_config["simulator"]["seed"])
    # if seed is -1, generate a cryptographically strong one
    if sim_seed == -1:
        import secrets

        sim_seed = secrets.randbelow(1_000_000_000)

    sim_use_padding = bool(yml_config["simulator"]["use_padding"])
    sim_max_placement_time = int(yml_config["simulator"]["max_placement_time"])

    temp_file_prefix = str(yml_config["simulator"]["output_file_prefix"])

    # file prefix is 'report' if the used doesn't write it
    file_prefix = "report" if temp_file_prefix == "" else temp_file_prefix
    datetime_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_basename = file_prefix + " " + datetime_str + ".json"
    file_path = os.path.join(gc.REPORT_DIR, file_basename)

    # create report folder if it doesn't exist
    os.makedirs(gc.REPORT_DIR, exist_ok=True)

    sim_report_output_file = file_path

    # SIMULATOR CHECKS

    if sim_num_of_epochs < 1:
        logger.error("Number of epochs must be greater or equal 1")
        return False

    if sim_function_duration < 1:
        logger.error("Function duration must be greater or equal 1")
        return False

    if sim_seed < -1:
        logger.error("Simulator seed must be -1 (ignore seed) or greater or equal 0")
        return False

    if sim_max_placement_time < 1:
        logger.error("Max placement time must be greater or equal 1 (seconds)")
        return False

    # EVENTS

    event_generator_trigger_probability = float(
        yml_config["events"]["generator_trigger_probability"]
    )
    event_min_probability = float(yml_config["events"]["event_min_probability"])
    event_max_probability = float(yml_config["events"]["event_max_probability"])

    # EVENTS CHECK

    if (
        event_generator_trigger_probability > 1
        or event_generator_trigger_probability < 0
    ):
        logger.error("Probability of trigger generator must be a value between 0 and 1")
        return False

    if event_min_probability > 1 or event_min_probability < 0:
        logger.error(
            "Minimum probability of event trigger must be a value between 0 and 1"
        )
        return False

    if event_max_probability > 1 or event_max_probability < 0:
        logger.error(
            "Minimum probability of event trigger must be a value between 0 and 1"
        )
        return False

    if event_min_probability > event_max_probability:
        logger.error(
            "Minimum probability of event trigger can't be greater than maximum probability"
        )
        return False

    # INFRASTRUCTURE

    infr_type = str(yml_config["infrastructure"]["type"])
    if not infr_type in ["physical", "logical"]:
        logger.error(
            "Only allowed value for infrastructure type are 'physical' and 'logical'"
        )
        return False

    infr_is_dynamic = bool(yml_config["infrastructure"]["is_dynamic"])

    if infr_is_dynamic:

        # Node crash and resurrection probabilities

        infr_node_crash_probability = dict(
            yml_config["infrastructure"]["crash_probability"]
        )
        infr_node_resurrection_probability = dict(
            yml_config["infrastructure"]["resurrection_probability"]
        )

        for key in ["cloud", "fog", "edge"]:
            if key not in infr_node_crash_probability:
                logger.error(
                    f"{key} is missing from infrastructure node crash probability"
                )
                return False
            if key not in infr_node_crash_probability:
                logger.error(
                    f"{key} is missing from infrastructure node resurrection probability"
                )
                return False

        # Link crash and resurrection probabilities

        infr_link_crash_probability = float(
            yml_config["infrastructure"]["link_crash_probability"]
        )
        infr_link_resurrection_probability = float(
            yml_config["infrastructure"]["link_resurrection_probability"]
        )
    else:

        # infrastructure is static -> no crashes or resurrections

        infr_node_crash_probability = {"edge": 0, "fog": 0, "cloud": 0}
        infr_node_resurrection_probability = {"edge": 0, "fog": 0, "cloud": 0}
        infr_link_crash_probability = 0
        infr_link_resurrection_probability = 0

    infr_energy = dict(yml_config["infrastructure"]["energy"])

    # APPLICATIONS

    applications = dict(yml_config["applications"])

    # APPLICATIONS CHECKS

    for app_name in applications:
        app = applications[app_name]
        application_filename = app["filename"]
        application_path = os.path.join(gc.APPLICATIONS_DIR, application_filename)
        if not os.path.isfile(application_path):
            logger.error(f"{app_name} application path is not a file")
            return False

    return True
