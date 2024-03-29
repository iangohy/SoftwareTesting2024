import argparse
import logging
import configparser
import time
from pathlib import Path

from oracle.oracle import Oracle
from greybox_fuzzer.main_fuzzer import MainFuzzer
from smart_fuzzer.input_models.djangoDict import DjangoDict
from smart_fuzzer.smartChunk import SmartChunk

REQUIRED_KEYS = {
    "target_application": ["name", "command", "log_folderpath", "test_driver", "coverage"],
    "main_fuzzer": ["max_fuzz_cycles", "mode"]
}

logger = logging.getLogger(__name__)
start_time = time.time()

parser = argparse.ArgumentParser(
            prog='python3 sudifuzz.py',
            description='Fuzzing program for CoAP, Django and BLE')
parser.add_argument('--config', dest='config', action='store',
            required=True, help='filepath of configuration .ini file')

args = parser.parse_args()

# Read configuration file
# Defaults for keys are also set here (if required)
config = configparser.ConfigParser()
config.read(args.config)

# == Create log folder if doesn't exist
log_folderpath = config.get("target_application", "log_folderpath")
log_filepath = f"{log_folderpath}/sudifuzz_{int(time.time())}.log"
Path(config["target_application"]["log_folderpath"]).mkdir(parents=True, exist_ok=True)

# === Set up logging
streamhandler = logging.StreamHandler()
filehandler = logging.FileHandler(log_filepath)
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", 
    level=logging.DEBUG,
    handlers=[
        filehandler,
        streamhandler
    ]
)

logger.info("================")
logger.info("Sudifuzzzzzzzzz")
logger.info("================")

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
        except KeyError:
            errors.append((section, key))
            
logger.debug(f"Errors: {errors}")
if len(errors) > 0:
    logger.info("\n\n===== CONFIG FILE ERRORS =====")
    for error in errors:
        logger.info(f"Section: [{error[0]}], Key: [{error[1]}]")
    exit()

# == Initialise components
oracle = Oracle(config["target_application"], config["django_testdriver"])
# TODO: Determine if we still need oracle initiated target application
# oracle.start_target_application_threaded()
# time.sleep(1)

# == Chunk Preprocessing
# Validate filepaths and generate chunks
seed_chunk = SmartChunk(DjangoDict(), "http://127.0.0.1:8000/api/product/delete/")
seed_chunk.get_chunks("http://127.0.0.1:8000/api/product/delete/")
seedQ = [seed_chunk]

# == Main Fuzzer
max_fuzz_cycles = config.getint("main_fuzzer", "max_fuzz_cycles")
mode = config.get("main_fuzzer", "mode")
logger.debug(f"max_fuzz_cycles={max_fuzz_cycles}, mode={mode}")
try:
    main_fuzzer = MainFuzzer(
        seedQ,
        oracle,
        max_fuzz_cycles=max_fuzz_cycles,
        mode=mode
    )
    seedQ, failureQ = main_fuzzer.fuzz()
except Exception as e:
    logger.exception(e)

logger.info("===========")
logger.info("Closing oracle")
# TODO: Proper oracle closing handling
oracle.signal_handler()
logger.info("===========")
logger.info("Sudifuzz exited")
end_time = time.time()
logger.info("Time taken: " + str(end_time - start_time))
logger.info("===========")