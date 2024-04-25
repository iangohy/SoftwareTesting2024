#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import logging
from subprocess import Popen, PIPE, STDOUT
import logging
import os
import binascii
import json
import hashlib
from smart_fuzzer.schunk import SChunk
from testdriver.utils import sanitize_input, clean_gen_files
from testdriver.custom_exceptions import TestDriverCrashDetected
import time

logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO)

class BluetoothTestDriver():
    def __init__(self, config, log_folderpath):
        self.bluetooth_dir = config.get("bluetooth_dir")
        self.coverage_mode = config.get("coverage_mode", "hash")
        self.log_folderpath = log_folderpath
        clean_gen_files()
        
    def run_coverage(self, mode='hash'):
        # TODO implement modes
        command = f"lcov --capture --directory {self.bluetooth_dir} --output-file {self.bluetooth_dir}/lcov.info -q --rc lcov_branch_coverage=1"
        os.system(command)
        logging.info('[OK] Coverage Done')
        
        command = f"lcov --rc lcov_branch_coverage=1 --summary {self.bluetooth_dir}/lcov.info"
        process = Popen(command, stdout=PIPE, stderr=STDOUT, text=True, shell=True, start_new_session=True)
        while True:
            line = process.stdout.readline()
            if line:
                logger.info(f"OUTPUT: {line}")
            if process.poll() is not None:
                break 
        # os.remove(f"{self.bluetooth_dir}lcov.info")
        logging.info('[OK] Summary Done')

        is_interesting, cov_data = self.is_interesting(mode)
        logging.info("Is it interesting? {}".format(is_interesting))

        # response = None
        
        # TODO: add cleanup (delete temporary file)
        # with open("bluetooth_fuzz.log") as f:
        #     response = {"status_code": f.readline()}
        # response.update(cov_data) 
        
        return (False, is_interesting, cov_data)
    
    def find_and_delete_gcda(self, directory):
        """
        Recursively find .gcda files within directories and delete them if present.
        """
        
        logger.debug("Deleting GCDA Files")
        # Check if .gcda files exist in the current directory
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isfile(item_path) and item.endswith('.gcda'):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                self.find_and_delete_gcda(item_path)

    
    def generate_code_with_test(self, handle, payload):
        # CLEAN gcda files
        dir_name = self.bluetooth_dir + "/build"
        self.find_and_delete_gcda(dir_name)
        
        with open(os.getcwd()+'/testdriver/bluetooth_template.py', 'r') as file:
            filedata = file.read()

        filedata = filedata.replace('|replace_handle|', sanitize_input(str(handle)))
        
        #  convert string to bytes
        input_bytes = payload.encode()
        #  covert bytes to hexadecimal 
        hex_input = binascii.hexlify(input_bytes).decode()
        filedata = filedata.replace('|replace_byte|', "0x"+str(hex_input))
        
        filedata = filedata.replace('|bluetooth_dir|', self.bluetooth_dir)        

        # Write the file out again
        with open(f'{self.bluetooth_dir}/bluetooth_fuzz.py', 'w') as file:
            file.write(filedata)
    
    def run_test(self, chunk: SChunk, coverage, test_number):  
          
        handle = chunk.get_lookup_chunk("handle").get_content()
        payload = chunk.get_lookup_chunk("payload").get_content()
        logger.info(f"handle: {handle}")
        # logger.info(f"payload: {payload:.50s}")
        logger.info(f"payload: {payload}")
        
        # Generate python file with inputs
        self.generate_code_with_test(handle, payload)
        
        command = f"python3 {self.bluetooth_dir}/bluetooth_fuzz.py"
        process = Popen(command, stdout=PIPE, stderr=STDOUT, text=True, shell=True, start_new_session=True)
        try:
            if test_number is not None:
                filename = f"{self.log_folderpath}/bluetooth_testdriver_{test_number}.log"
            else:
                filename = f"{self.log_folderpath}/bluetooth_testdriver_{int(time.time())}.log"
            with open(filename, "w") as file:
                self.process_stdout(process, file)
        except TestDriverCrashDetected as e:
            logger.exception(e)
            logger.error(f"Test driver crashed while running test case: {handle}, {payload}")
            # Failure true
            return (True, False, {})
        
        if coverage:
            Failure, is_interesting, information = self.run_coverage(mode=self.coverage_mode)
            
            logger.info(f"run_test return info: {information}")
            return Failure, is_interesting, information
        
    
    def process_stdout(self, process: Popen, logfile):
        logger.info("Handling target application stdout and stderr")
        while True:
            line = process.stdout.readline()
            if line:
                logger.info(f"OUTPUT: {line}")
                logfile.write(line)
            if process.poll() is not None:
                break 
        
        logger.info("===END===")
    
    def parse_lcov_lines(self, lines:list[str]):
        count = 0
        array = [{}]
        totalno_missing_branches = 0
        output_dict = {}
        # Strips the newline character
        for line in lines:
            line = line.strip()
            splitline = line.split(":")
            if splitline[0] == "SF":
                array[count]["SF"] = splitline[1]
                array[count]["Branch"] = []

            if splitline[0] == "BRDA":
                if "Branch" in array[count].keys():
                    brda = splitline[1].split(",")
                    # If count is zero
                    if brda[3] == "-" or 0:
                        array[count]["Branch"].append([brda[0], brda[1]])
                else:
                    array[count]["Branch"] = []
                    brda = splitline[1].split(",")
                    # If count is zero
                    if brda[3] == "-" or 0:
                        array[count]["Branch"].append([brda[0], brda[1]])
                    
            if splitline[0] == "end_of_record":
                array.append({})
                count += 1

        for i in range(0, count):
            filename = array[i]['SF']
            branches = array[i]['Branch']
            if len(branches) > 0:
                # remove duplicate branches
                b_set = set(map(tuple,branches))
                b = list(map(list,b_set))
                
                totalno_missing_branches += len(b)
                output_dict.update({filename: b})

        sorted_output_dict = {key: output_dict[key] for key in sorted(output_dict)}

        return sorted_output_dict, totalno_missing_branches

    def is_interesting(self, mode:str = 'hash'):
        # Store the new missing branches from the report
        new_missing_branches = {}
        totalno_missing_branches = 0
        distance = 0

        # Opens the coverage JSON report
        try:
            f = open('/ble/lcov.info', 'r')
            lines = f.readlines()
            new_missing_branches, totalno_missing_branches = self.parse_lcov_lines(lines)
            f.close()
        except Exception:
            logging.error("Cannot open output file")

        is_interesting_result = False
        return_object = {}
        
        # If missing branches store file exists
        if os.path.exists(os.getcwd()+'/testdriver/missing_branches.json'):

            # Open it and store the current missing branches
            try:
                f = open(os.getcwd()+'/testdriver/missing_branches.json', 'r')
                current_missing_branches:dict = json.loads(f.read())
                f.close()
            except Exception:
                logging.error("Cannot open missing branch file")

            if mode == 'distance' and 'path_history' not in current_missing_branches:
                # If it finds that the number of files with missing branches is less than the current number
                # That means we have fewer missing branches to cover
                # That is interesting!
                if len(new_missing_branches.keys()) < len(current_missing_branches.keys()):
                    is_interesting_result = True

                # For each file index within the missing branch store
                for i in range( min( len(current_missing_branches.keys()), len(new_missing_branches.keys()) ) ):

                    file = list(current_missing_branches.keys())[i]

                    # Find the intersection / common branches between the current and new
                    # We label them as the leftover branches that are still missing
                    leftover_branches = self.find_common_elements(
                        list(current_missing_branches.values())[i],
                        list(new_missing_branches.values())[i],
                    )

                    # If we find that the leftover branches are fewer than the current missing branches
                    # That means we have fewer missing branches to cover
                    # That is interesting!
                    if len(leftover_branches) < len(list(current_missing_branches.values())[i]):
                        is_interesting_result = True
                        # Add the number of branch difference to our distance metric
                        distance += len(list(current_missing_branches.values())[i]) - len(leftover_branches)

                    # Assign the leftover branches to the file to be looked over the next coverage test
                    current_missing_branches[file] = leftover_branches

                    f = open(os.getcwd()+'/testdriver/missing_branches.json', 'w')
                    f.write(json.dumps(current_missing_branches))
                    f.close()

                    return_object = { 'dist': distance }
            elif mode == 'hash' and 'path_history' in current_missing_branches:
                # Get a Path ID as a hashed version of the missing branches object
                new_path_ID = hashlib.md5( json.dumps(new_missing_branches).encode() ).hexdigest()

                # Fetch the path history as a list of hashed path IDs
                path_history:list = current_missing_branches['path_history']
                
                if new_path_ID not in path_history:
                    # A new path!
                    is_interesting_result = True
                    path_history.append(new_path_ID)

                    # Update the output JSON file
                    f = open(os.getcwd()+'/testdriver/missing_branches.json', 'w')
                    f.write( json.dumps({
                        'path_history': path_history
                    }) )
                    f.close()

                # Return the path ID regardless
                return_object = { 'hash': new_path_ID }
            else:
                logging.error('Invalid mode operation!')
        
        # If the missing branches json doesn't exist
        else:
            # By default consider the result interesting
            is_interesting_result = True

            # Begin storing the missing branches
            f = open(os.getcwd()+'/testdriver/missing_branches.json', 'w')

            if mode == 'distance':
                f.write( json.dumps(new_missing_branches) )
                return_object = { 'dist': totalno_missing_branches }
            else:
                # Get a Path ID as a hashed version of the missing branches object
                path_ID = hashlib.md5( json.dumps(new_missing_branches).encode() ).hexdigest()

                # Start saving a history of paths checked
                f.write( json.dumps({
                    'path_history':[ path_ID ]
                }) )

                return_object = { 'hash': path_ID }

            f.close()

        return (is_interesting_result, return_object)

    def find_common_elements(self, list1, list2):
        return [element for element in list1 if element in list2]
    
# Usage
if __name__ == "__main__": 
    inputs = ["0x00001"]
    # Example
    for i in range(len(inputs)):
        driver = BluetoothTestDriver("../SoftwareTestingRepo/bluetooth/")
        driver.run_test(inputs[i], True)
        