#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import logging
from subprocess import Popen, PIPE, STDOUT
import logging
import shutil
import os

logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO)

class BluetoothTestDriver():
    def __init__(self, config):
        self.bluetooth_dir = config.get("bluetooth_dir")
        
    def move_flash_bin(self):
        try:
            shutil.copyfile("./flash.bin", self.bluetooth_dir+"flash.bin")
        except FileNotFoundError:
            logging.info("File not found.")
        except PermissionError:
            logging.info("Permission denied.")
        except Exception as e:
            logging.info(f"An error occurred: {e}")
        
    def run_coverage(self):
        command = f"lcov --capture --directory {self.bluetooth_dir} --output-file {self.bluetooth_dir}lcov.info -q --rc lcov_branch_coverage=1"
        os.system(command)
        logging.info('[OK] Coverage Done')
        
        command = f"lcov --rc lcov_branch_coverage=1 --summary {self.bluetooth_dir}lcov.info"
        process = Popen(command, stdout=PIPE, stderr=STDOUT, text=True, shell=True, start_new_session=True)
        while True:
            line = process.stdout.readline()
            if line:
                logger.info(f"OUTPUT: {line}")
            if process.poll() is not None:
                break 
        # os.remove(f"{self.bluetooth_dir}lcov.info")
        logging.info('[OK] Summary Done')
    
    def generate_code_with_test(self, chunk):
        with open(os.getcwd()+'/testdriver/bluetooth_template.py', 'r') as file:
            filedata = file.read()

        # Replace the target string
        filedata = filedata.replace('|replace_handle|', chunk.children[0].get_content())
        filedata = filedata.replace('|replace_byte|', str(chunk.children[1].get_content().encode()))
        filedata = filedata.replace('|bluetooth_dir|', self.bluetooth_dir)        

        # Write the file out again
        with open(f'{self.bluetooth_dir}bluetooth_fuzz.py', 'w') as file:
            file.write(filedata)
    
    def run_test(self, inputs, coverage: bool):        
        # Generate python file with inputs
        self.generate_code_with_test(inputs)
        
        command = f"python3 {self.bluetooth_dir}bluetooth_fuzz.py"
        with open("bluetooth_fuzz.log", "a") as logfile:
            try:
                process = Popen(command, stdout=PIPE, stderr=STDOUT, text=True, shell=True, start_new_session=True)
                self.process_stdout(process, logfile)
            except Exception as e:
                logger.info(f"ERROR: {e}")
        if coverage:
            self.run_coverage()
    
    def process_stdout(self, process: Popen, logfile):
        logger.info("Handling target application stdout and stderr")
        while True:
            line = process.stdout.readline()
            if line:
                logger.info(f"OUTPUT: {line}")
                logfile.write(line)
            if process.poll() is not None:
                break 
        
        # move flash.bin to bluetooth folder
        # self.move_flash_bin()
        logger.info("===END===")
    
    def analyze_results(self, response):
        # Analyze the results of the server response
        pass
    
    def interpret(self, input_data):
        # interpret ASCII to fit to request
        
        return 0
    
# Usage
if __name__ == "__main__": 
    inputs = ["0x00001"]
    # Example
    for i in range(len(inputs)):
        driver = BluetoothTestDriver("../SoftwareTestingRepo/bluetooth/")
        driver.run_test(inputs[i], True)
        