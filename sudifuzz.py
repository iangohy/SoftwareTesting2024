# from oracle.oracle import Oracle
# import time
import argparse
import logging
import configparser

from oracle.oracle import Oracle
from greybox_fuzzer.main_fuzzer import MainFuzzer
from smart_fuzzer.input_models.djangoDict import DjangoDict
from smart_fuzzer.smartChunk import SmartChunk

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
# TODO: pass in oracle configuration once oracle package has been updated
oracle = Oracle(config["target_application"])

# == Chunk Preprocessing
# - Configuration file (general): This configuration file is for the entire sudifuzz program
# - Chunks: XML structure, seed input..., filepaths should be defined in configuration file
# Validate filepaths and generate chunks
seed_chunk = SmartChunk(DjangoDict(), "http://127.0.0.1:8000/api/product/delete/")
seed_chunk.get_chunks("http://127.0.0.1:8000/api/product/delete/")
seedQ = [seed_chunk]

# == Main Fuzzer
try:
    main_fuzzer = MainFuzzer(seedQ, oracle)
    seedQ, failureQ = main_fuzzer.fuzz()
except Exception as e:
    logger.exception(e)

logger.info("===========")
logger.info("Sudifuzz exited")