import argparse
import logging
import configparser
import time
from pathlib import Path
import copy

from greybox_fuzzer.stats_collector import StatsCollector
from oracle.oracle import Oracle
from greybox_fuzzer.main_fuzzer import MainFuzzer
from smart_fuzzer.chunkTreeGenerator import ChunkTreeGenerator

REQUIRED_KEYS = {
    "target_application": ["name", "log_folderpath", "test_driver", "coverage", "seed_input_files"],
    "main_fuzzer": ["max_fuzz_cycles", 'energy_strat']
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
log_folderpath = config.get("target_application", "log_folderpath") + f"/sudifuzz_{int(time.time())}"
log_filepath = f"{log_folderpath}/sudifuzz.log"
Path(log_folderpath).mkdir(parents=True, exist_ok=True)

# === Set up logging
streamhandler = logging.StreamHandler()
filehandler = logging.FileHandler(log_filepath)
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", 
    level=logging.INFO,
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
    config_file_errors = "\n\n===== CONFIG FILE ERRORS =====\n"
    for error in errors:
        config_file_errors += f"Section: [{error[0]}], Key: [{error[1]}]\n"
    logger.info(config_file_errors)
    exit()

# == Initialise components
oracle = Oracle(config, log_folderpath)
# TODO: Determine if we still need oracle initiated target application
# oracle.start_target_application_threaded()
# time.sleep(1)

# == Chunk Preprocessing
# Validate filepaths and generate chunks
seedQ = []
seed_files = config.get("target_application", "seed_input_files").split(",")
for seed_file in seed_files:
    logger.info(f"Processing seed file {seed_file}")
    # Check if file exists
    if not Path(seed_file).is_file():
        raise RuntimeError(f"Error processing seed file: {seed_file}")
    tree_generator = ChunkTreeGenerator(seed_file)
    chunk_root = tree_generator.generate_chunk_tree()
    seedQ.append((copy.deepcopy(chunk_root), None))
logger.info(f"Initial seedQ: {seedQ}")

# == Main Fuzzer
max_fuzz_cycles = config.getint("main_fuzzer", "max_fuzz_cycles")
energy_strat = config.get("main_fuzzer", "energy_strat")
logger.debug(f"max_fuzz_cycles={max_fuzz_cycles}, energy_strat={energy_strat}")
try:
    stats_collector = StatsCollector(log_folderpath)
    main_fuzzer = MainFuzzer(
        seedQ,
        oracle,
        stats_collector,
        max_fuzz_cycles=max_fuzz_cycles,
        energy_strat=energy_strat,
    )
    main_fuzzer.fuzz()
except KeyboardInterrupt:
        logger.info("Keyboard interrupt detected")
except Exception as e:
    logger.exception(e)
finally:
    stats_collector.log_current_stats()
    stats_collector.plot_crashes()
    stats_collector.plot_is_interesting()

end_time = time.time()
exited_string = "\n===========\n" + \
    "Sudifuzz exited\n" + \
    f"Sudifuzz ran for : {str(end_time - start_time)}s\n" + \
    "==========="
logger.info(exited_string)