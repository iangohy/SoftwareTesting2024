# from oracle.oracle import Oracle
# import time
import argparse
import logging
import configparser

from oracle.oracle import Oracle

logger = logging.getLogger(__name__)

streamhandler = logging.StreamHandler()
filehandler = logging.FileHandler("sudifuzz.log")
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", 
    level=logging.DEBUG,
    handlers=[
        filehandler,
        streamhandler
    ]
)

parser = argparse.ArgumentParser(
            prog='python3 sudifuzz.py',
            description='Fuzzing program for CoAP, Django and BLE')
parser.add_argument('--config', dest='config', action='store',
            required=True, help='filepath of configuration .ini file')

args = parser.parse_args()
logger.info("================")
logger.info("Sudifuzzzzzzzzz")
logger.info("================")
logger.info(f"Configuration Filepath: {args.config}")

# Verify configuration file
config = configparser.ConfigParser()
config.read(args.config)

REQUIRED_KEYS = {
    "target_application": ["name", "command", "log_filepath"]
}
errors = []
# Find section and validate keys
for section, keys in REQUIRED_KEYS.items():
    logger.debug(f"Verifying section [{section}]")
    for key in keys:
        logger.debug(f"Verifying key {key}")
        try:
            config_value = config[section][key]
            if config_value is None:
                errors.append((section, key))
            else:
                logger.debug(f"Found [{section}][{key}]:{config_value}")
        except KeyError:
            errors.append((section, key))
            
logger.debug(f"Errors: {errors}")
if len(errors) > 0:
    logger.info("\n\n===== CONFIG FILE ERRORS =====")
    for error in errors:
        logger.info(f"Section: [{error[0]}], Key: [{error[1]}]")
    exit()

# == Initialise components
seedQ = []
failureQ = []
# TODO: pass in oracle configuration once oracle package has been updated
oracle = Oracle("sudifuzz_config_example.ini")

# == Chunk Preprocessing
# - Configuration file (general): This configuration file is for the entire sudifuzz program
# - Chunks: XML structure, seed input..., filepaths should be defined in configuration file
# Validate filepaths and generate chunks

# == Main Fuzzer
cycle_num = 1
try:
    logger.info(f"Main Fuzzer Cycle {cycle_num}")
    # Main fuzzer code goes here
    # seedQ, failureQ = main_fuzzer(seedQ, failureQ, oracle)
    cycle_num += 1
except Exception as e:
    logger.exception(e)
    # Save states -> seedQ, failureQ

logger.info("===========s")
logger.info("Sudifuzz exited")