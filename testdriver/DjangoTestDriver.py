import requests
import logging
import json
import os
import random
import hashlib
from subprocess import Popen, PIPE, STDOUT
import time

from smart_fuzzer.schunk import SChunk
from testdriver.custom_exceptions import TestDriverCrashDetected
from testdriver.utils import check_for_blacklist_phrase
from testdriver.utils import sanitize_input
logger = logging.getLogger(__name__)

class DjangoTestDriver:
    def __init__(self, config):
        self.server_url = "http://127.0.0.1:8000/"
        self.endpoints = ["api/product/", "datatb/product/add/", "datatb/product/edit/",
                "datatb/product/delete/", "datatb/product/export/", "accounts/register/", "accounts/login/"]
        self.django_dir = config.get("django_dir")
        self.coverage_mode = config.get("coverage_mode", "distance")

    # Oracle will pass in chunk as test input
    def run_test(self, chunk: SChunk, coverage: bool = False):
        logger.debug(f"Received chunk: {chunk}")
        endpoint = chunk.get_lookup_chunk("endpoint").get_content()
        payload = chunk.get_lookup_chunk("payload").get_content()
        for i in payload:
            logger.info(payload[i])
            payload[i] = payload[i].chunk_content
        logger.info(f"payload: {payload}")

        # TODO: update input data with actual data from chunk
        return self.send_request_with_interesting(
            endpoint=endpoint,
            input_data=payload,
            method='post',
            coverage=coverage,
            mode=self.coverage_mode
        )
    
    def send_request(self, input_data):
        """
        Call interpret function to get readable inputs
         - input_data, headers = self.interpret(input_data)
        
        Note: Fuzzing formData and header
         - input_data["formData"] and input_data["headers"]
        """
                
        ### example input
        data_input = {
            'name': input_data["NAME"],
            'info': input_data["INFO"],
            'price': input_data["PRICE"]
        }
        
        data_input = json.dumps(data_input)
        method = input_data["METHOD"]
        headers = {}
        ################
        try:
            if method == "post":
                response = requests.post(input_data["ENDPOINT"], data=input_data, headers=headers)
            elif method == "get":
                response = requests.get(input_data["ENDPOINT"], data=input_data, headers=headers)
            elif method == "delete":
                response = requests.delete(input_data["ENDPOINT"], data=input_data, headers=headers)
            elif method == "put":
                response = requests.put(input_data["ENDPOINT"], data=input_data, headers=headers)
            logging.debug(response.status_code)
            return {"status_code": response.status_code}
        except Exception as ex:            
            logging.error(ex)
            
    
    def send_request_with_interesting(self, 
            # Default input config
            endpoint,
            input_data={'name': "hello",'info': "bye",'price': str(1)}, 
            method="get", # post | get | put | delete | patch
            coverage=False,
            mode="hash"
        ):
        """
        Call interpret function to get readable inputs
         - input_data, headers = self.interpret(input_data)
        
        Note: Fuzzing formData and header
         - input_data["formData"] and input_data["headers"]
        """
        
        text_to_replace = {
            # endpoint should not need "/" in front
            "ENDPOINT":  sanitize_input(endpoint),
            "FORM_DATA": sanitize_input(input_data),
            "METHOD":    sanitize_input(method)
        }

        # Reads the current template file
        try:
            f = open(os.getcwd()+"/testdriver/template_test.py", 'r')
            data = f.read()
            f.close()
        except Exception as ex:
            logging.error(ex)

        # Replaces all keywords from text_to_replace
        for var in text_to_replace.keys():
            data = data.replace('|{}|'.format(var), text_to_replace[var])

        # Writes new TestCase for Django
        f = open(os.getcwd()+"/testdriver/test_case.py", 'w')
        f.write(data)
        f.close()
    
        if coverage:
            # Runs the coverage command on the Django directory and generates a JSON report
            command = "coverage3 run --branch --omit='tests.py' {}/manage.py test testdriver/; coverage3 json --pretty-print -o {}".format(self.django_dir, os.getcwd()+'/testdriver/output.json')
            logger.debug(f"Running command: {command}")
            process = Popen(command, stdout=PIPE, stderr=STDOUT, text=True, shell=True, start_new_session=True)
            try:
                with open(f"logs/django_testdriver_{int(time.time())}.log", "w") as file:
                    self.process_stdout(process, file)
            except TestDriverCrashDetected as e:
                logger.exception(e)
                logger.error(f"Test driver crashed while running test case: {input_data}")
                # TODO: determine return values on crash
                return

            is_interesting, cov_data = self.is_interesting(mode)
            logging.info("Coverage run complete for {}".format(text_to_replace))
            logging.info("Is it interesting? {}".format(is_interesting))
            
            response = None
            # TODO: add cleanup (delete temporary file)
            with open("fuzz.log") as f:
                response = {"status_code": f.readline()}
            response.update(cov_data)
            return (False, is_interesting, response)
        else:
            # Runs the standard manage.py test command, look for tests in testdriver folder
            # os.system("python3 {}manage.py test testdriver/".format(self.django_dir))
            logging.info("Run complete for {}".format(text_to_replace))
            return self.send_request(text_to_replace)


    def analyze_results(self, response):
        # Analyze the results of the server response
        pass
    
    def interpret(self, input_data):
        # interpret ASCII to fit to request
        
        return 0
    
    def is_interesting(self, mode:str = 'hash'):
        # Opens the coverage JSON report
        try:
            f = open(os.getcwd()+'/testdriver/output.json', 'r')
            coverage_data = json.loads(f.read())
            f.close()
        except Exception:
            logging.error("Cannot open output file")

        is_interesting_result = False
        return_object = {}
        
        # Store the new missing branches from the report
        new_missing_branches = {}
        totalno_missing_branches = 0
        distance = 0
        
        # Fetch the missing branches field from each file
        for file in coverage_data['files'].keys():
            
            # If a file does not contain any missing branches, we skip
            if coverage_data['files'][file]['summary']['missing_branches'] <= 0:
                continue
            new_missing_branches[file] = coverage_data['files'][file]['missing_branches']
            totalno_missing_branches += coverage_data['files'][file]['summary']['missing_branches']

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
                # For each file index within the missing branch store
                for i in range(len(current_missing_branches.keys())):

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

    def clean(self):
        if os.path.exists(os.getcwd()+'/testdriver/missing_branches.json'):
            os.remove(os.getcwd()+'/testdriver/missing_branches.json')
        else:
            logging.error("The directory is already clean")
                
    def process_stdout(self, process: Popen, logfile):
        logger.info("Handling target application stdout and stderr")
        # Case ignored
        blacklist = ["segmentation fault", "core dumped"]
        logger.debug(f"Blacklist is: {blacklist}")

        while True:
            # if self.exit_event.is_set():
            #     raise KeyboardInterrupt()
            os.set_blocking(process.stdout.fileno(), False)
            # line = non_block_read(process.stdout)
            line = process.stdout.readline()
            if line:
                logger.debug(f"OUTPUT: {line}")
                if logfile:
                    logfile.write(line)
                check_for_blacklist_phrase(line, blacklist)
            if process.poll() is not None:
                break

        status = process.poll()
        if status != 0:
            raise TestDriverCrashDetected(f"Process exited with signal {process.poll()}")
        else:
            logger.debug("Process exited with status 0")

# Usage
if __name__ == "__main__":  
    
    # Configuration
    DJANGO_DIRECTORY = '../DjangoWebApplication/'

    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG) 

    driver = DjangoTestDriver(
        django_dir=DJANGO_DIRECTORY
    )
    # driver.run_test(None, True)

    # Crashing test
    driver.send_request_with_interesting(
        endpoint="/datatb/product/add/",
        input_data={
            # Default fuzzing implementation
            'name': ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', k=10)),
            'info': ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', k=2000)),
            'price': str(random.randint(1, 100)),
        },
        method='post',
        coverage=True
    )