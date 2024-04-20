import time
import logging
import signal
import threading

from smart_fuzzer.schunk import SChunk
from testdriver.BluetoothTestDriver import BluetoothTestDriver
from testdriver.DjangoTestDriver import DjangoTestDriver
from testdriver.CoapTestDriver import CoapTestDriver

logger = logging.getLogger(__name__)

class Oracle:
    def __init__(self, config, log_folderpath):
        self.target_app_config = config["target_application"]
        self.is_crashed = threading.Event()
        self.exit_event = threading.Event()
        self.coverage = self.target_app_config.getboolean("coverage")
        self.logfile = f'{log_folderpath}/{self.target_app_config["name"]}_{int(time.time())}.log'
        self.log_folderpath = log_folderpath


        config_testdriver = self.target_app_config.get("test_driver")
        if config_testdriver == "DjangoTestDriver":
            self.test_driver = DjangoTestDriver(config["django_testdriver"], self.log_folderpath)
        elif config_testdriver == "CoapTestDriver":
            self.test_driver = CoapTestDriver(config["coap_testdriver"], self.log_folderpath)
        elif config_testdriver == "BluetoothTestDriver":
            self.test_driver = BluetoothTestDriver(config["bluetooth_testdriver"], self.log_folderpath)
        else:
            raise RuntimeError(f"Invalid test driver constant [{config_testdriver}]")

    # Runs the test and returns True if successful and False if crash
    def run_test(self, chunk: SChunk, test_number):
        """Sends test input SmartChunk to test driver. Returns failed, isInteresting, additional_info_dict"""
        response = self.test_driver.run_test(chunk, self.coverage, test_number)
        logger.debug(f"Response from testdriver: {response}")
        return response
    
if __name__ == "__main__":
    # 1. Create Oracle
    # 2. Start target application
    #   - Oracle will start application
    # 3. Run test
    # 4. Oracle will check if program has crashed before returning test result
    # 5. If no crash, return pass and continue. If crash, return fail and restart application

    oracle = Oracle("target_toy_app_config.ini")
    oracle.start_target_application_threaded()

    time.sleep(3)
    failures = 0
    for i in range(10):
        logger.info(f"Running test with input {i}")
        res = oracle.run_test(i)
        if not res:
            failures += 1

    logger.info(f"Total failures: {failures}")

    # Handle CTRL+C
    signal.signal(signal.SIGINT, oracle.signal_handler)