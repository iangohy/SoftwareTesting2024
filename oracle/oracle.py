from subprocess import Popen, PIPE, STDOUT
import time
import logging
import sys
import os
import signal
from oracle.custom_exceptions import OracleCrashDetected
import configparser
import threading
import requests

from oracle.utils import non_block_read

logger = logging.getLogger(__name__)

class Oracle:
    def __init__(self, configuration_filename):
        self.configuration_filename = configuration_filename
        config = configparser.ConfigParser()
        config.read(configuration_filename)
        self.target_app_config = config["target_application"]
        self.is_crashed = threading.Event()
        self.exit_event = threading.Event()

    def start_application_persistent(self):
        while True:
            self.start_target_application()
            logger.info(">>>>> Target application crashed, restarting...")

    def start_target_application(self):
        logger.info(f"Starting target application [{self.target_app_config['name']}]")
        self.run_command_and_log(self.target_app_config["command"], self.target_app_config["log_filepath"])
        logger.info(">>>>> Target application crashed")

    def start_target_application_threaded(self):
        t = threading.Thread(target=self.start_target_application).start()

    # Starts the target application
    # Target application will run until crash or child process is somehow stopped
    # TODO: Move to threaded implementation
    def run_command_and_log(self, command, log_filepath):
        logger.debug(f"[start_target_application] command={command}")
        logger.debug(f"[start_target_application] log_filepath={log_filepath}")
        process = None
        with open(log_filepath, "a") as logfile:
            try:
                process = Popen(command, stdout=PIPE, stderr=STDOUT, text=True, shell=True, start_new_session=True)
                logger.info("Target application started")
                crash = False
                self.process_stdout(process, logfile)
            except OracleCrashDetected as e:
                logger.info(f"CRASH DETECTED: {e}")
                logfile.write(">>> ORACLE DETECTED CRASH\n")
                self.is_crashed.set()
            finally:
                if process:
                    # Send SIGTERM to whole process group
                    try: 
                        logger.info("Sending SIGTERM to child process group")
                        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                    except ProcessLookupError:
                        pass

    def process_stdout(self, process: Popen, logfile):
        logger.info("Handling target application stdout and stderr")
        # Case ignored
        blacklist = ["segmentation fault", "core dumped"]
        logger.info(f"Blacklist is: {blacklist}")

        while True:
            if self.exit_event.is_set():
                raise KeyboardInterrupt()
            os.set_blocking(process.stdout.fileno(), False)
            # line = non_block_read(process.stdout)
            line = process.stdout.readline()
            if line:
                logger.info(f"OUTPUT: {line}")
                logfile.write(line)
                self.check_for_blacklist_phrase(line, blacklist)
            if process.poll() is not None:
                break

        # Will only reach here if crash
        raise OracleCrashDetected(f"Process exited with signal {process.poll()}")

    # Check for blacklisted word
    # throws OracleCrashDetected
    def check_for_blacklist_phrase(self, line: str, blacklist: list):
        logger.debug(f"Checking for blacklisted words in: {line}")
        for blacklist_phrase in blacklist:
                if blacklist_phrase.lower() in line.lower():
                    raise OracleCrashDetected(f"blacklist phrase [{blacklist_phrase}] detected")

    def signal_handler(self, signum, frame):
        logger.info("Setting exit_event")
        self.exit_event.set()

    # Runs the test and returns True if successful and False if crash
    def run_test(self, argument):
        # Send request
        try:
            r = requests.get(f"http://localhost:5000/{argument}")
            # If get, valid response, then is not crash
            if r.status_code == 200:
                time.sleep(1)
                return True
        except Exception:
            logger.error("Exception occurred in request")

        time.sleep(2)
        # Check if crash
        if self.is_crashed.is_set():
            logger.info("is_crashed set to True")
            self.is_crashed.clear()
            # Restart application
            self.start_target_application_threaded()
            return False
        else:
            logger.info("is_crashed set to False")
            return True

        return False


if __name__ == "__main__":
    # 1. Create Oracle
    # 2. Start target application
    #   - Oracle will start application
    # 3. Run test
    # 4. Oracle will check if program has crashed before returning test result
    # 5. If no crash, return pass and continue. If crash, return fail and restart application

    # oracle = Oracle("target_django_config.ini")
    # oraacle = Oracle("target_coap_config.ini")
    oracle = Oracle("target_toy_app_config.ini")
    # oracle.start_target_application()
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