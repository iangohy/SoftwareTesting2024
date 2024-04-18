from aiocoap import Context, Message, Code
import logging
import asyncio
import logging
import os
import json
import time
import signal
import hashlib
from subprocess import Popen, PIPE, STDOUT
from testdriver.utils import check_for_blacklist_phrase
from testdriver.custom_exceptions import TestDriverCrashDetected

from smart_fuzzer.schunk import SChunk

logger = logging.getLogger(__name__)
class CoapTestDriver:
    def __init__(self, config, log_folderpath):
        self.server_url = "coap://127.0.0.1:5683"
        self.endpoints = ['/basic', '/storage', '/child', '/separate', '/etag', '/', '/big', '/encoding', '/advancedSeparate', '/void', '/advanced', '/long', '/xml']
        self.coap_dir = config.get("coap_dir")
        self.coverage_mode = config.get("coverage_mode", "hash")
        self.logger = logging.getLogger(__name__)
        self.log_folderpath = log_folderpath
    
    # oracle to pass in 
    def run_test(self, chunk: SChunk, coverage, test_number):
        logger.info(self.__dict__)
        logger.info(chunk.__dict__)
        logger.info(f"Received chunk: {chunk}")
        code = chunk.get_lookup_chunk("code").get_content()
        endpoint = chunk.get_lookup_chunk("endpoint").get_content()
        payload = chunk.get_lookup_chunk("payload").get_content()
        logger.info(f"method: {code}")
        logger.info(f"endpoint: {endpoint}")
        logger.info(f"payload: {payload}")
        
        return self.send_request_with_interesting(
            code=code,
            endpoint=endpoint,
            input_data=payload,
            coverage=coverage,
            mode=self.coverage_mode,
            test_number=test_number
        )
            
    async def send_request(self, input_data):
        """
        Call interpret function to get readable inputs
         - input_data, headers = self.interpret(input_data)
        
        Note: Fuzzing Message code, uri, message type, payload, token, message id, options, version?
         - request = Message(code=input_data["code"], uri=input_data["url"], payload=input_data["payload"], mtype=input_data["mtype"], token=input_data["token"])
        """
        
        url = f"{self.server_url}{self.endpoints[0]}"
        
        # dummy
        request = Message(code=Code.GET, uri=url, payload=input_data, mtype=0, token=bytes("token",'UTF-8'))
        logging.debug(request.token)
        context = await Context.create_client_context()
        response = await context.request(request).response
        
        return response
    
    def send_request_with_interesting(self,
            # Default input config
            code,
            endpoint, 
            input_data:str = 'Hello world!',
            coverage=False,
            mode='hash',
            test_number=None
        ):
                
        text_to_replace = {
            # endpoint should not need "/" in front
            "CODE":  code,
            "URL": endpoint,
            "PAYLOAD": input_data,
            "TYPE": "0"
        }

        # Reads the current template file
        try:
            f = open(os.getcwd()+"/testdriver/coap_request.py", 'r')
            data = f.read()
            f.close()
        except Exception as ex:
            logging.error(ex)
            
        # Replaces all keywords from text_to_replace
        for var in text_to_replace.keys():
            data = data.replace('|{}|'.format(var), text_to_replace[var])

        # Writes new TestCase for Coap
        f = open(f"{self.coap_dir}/coap_test.py", 'w')
        f.write(data)
        f.close()

        if coverage:            
            command = "coverage2 run {}/coapserver.py -i 127.0.0.1 -p 5683".format(self.coap_dir)
            logger.info(f"Running command: {command}")
            process_one = Popen(command, stdout=PIPE, stderr=STDOUT, text=True, shell=True, start_new_session=True)            
                
            command = f"python2 {self.coap_dir}/coap_test.py"
            logger.info(f"Running command: {command}")
            process_two = Popen(command, stdout=PIPE, stderr=STDOUT, text=True, shell=True, start_new_session=True)
            
            
            try:
                if test_number is not None:
                    filename = f"{self.log_folderpath}/coap_testdriver_{test_number}.log"
                else:
                    filename = f"{self.log_folderpath}/coap_testdriver_{int(time.time())}.log"
                with open(filename, "w") as file:
                    self.process_stdout(process_two, file)
            except TestDriverCrashDetected as e:
                logger.exception(e)
                logger.error(f"Test driver crashed while running test case: {input_data}")
                # TODO: determine return values on crash
                # Failure true
                return (True, False, {})
            
            
            # WAIT FOR TEST CASE TO FINISH
            while process_two.poll() is None:            
                logger.info(f"Running")
            
            
            logger.info(f"Not running")
            os.killpg(os.getpgid(process_one.pid), signal.SIGTERM) 
            
            # WAIT FOR COAP SERVER TO END
            while process_one.poll() is None:            
                logger.info(f"Running")
                
            command = "coverage2 json --pretty-print -o {}".format(os.getcwd()+'/testdriver/output.json')
            logger.info(f"Running command: {command}")
            Popen(command, stdout=PIPE, stderr=STDOUT, text=True, shell=True, start_new_session=True)
            
            try:
                is_interesting, cov_data = self.is_interesting(mode)
            except Exception as e:
                # Failure true
                return (True, False, {})
            logging.info("Coverage run complete for {}".format(text_to_replace))
            logging.info("Is it interesting? {}".format(is_interesting))
            
            response = None
            try:
                with open("coap_fuzz.log") as f:
                    response = {"status_code": f.readline()}
            except FileNotFoundError:
                time.sleep(0.2)
                with open("coap_fuzz.log") as f:
                    response = {"status_code": f.readline()}
            response.update(cov_data)
            
            return (False, is_interesting, response)

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
                logger.info(f"OUTPUT: {line}")
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

        # Store the new missing lines from the report
        new_missing_lines = {}
        totalno_missing_lines = 0
        distance = 0
        
        # Fetch the missing lines field from each file
        for file in coverage_data['files'].keys():

            # If a file does not contain any missing lines, we skip
            if coverage_data['files'][file]['summary']['missing_lines'] <= 0:
                continue
            new_missing_lines[file] = coverage_data['files'][file]['missing_lines']
            totalno_missing_lines += coverage_data['files'][file]['summary']['missing_lines']

        # If missing lines store file exists
        if os.path.exists(os.getcwd()+'/testdriver/missing_lines.json'):

            # Open it and store the current missing lines
            try:
                f = open(os.getcwd()+'/testdriver/missing_lines.json', 'r')
                current_missing_lines:dict = json.loads(f.read())
                f.close()
            except Exception:
                logging.error("Cannot open missing lines file")
            
            if mode == 'distance' and 'path_history' not in current_missing_lines:
                # For each file index within the missing branch store
                for i in range(len(current_missing_lines.keys())):

                    file = list(current_missing_lines.keys())[i]

                    # Find the intersection / common lines between the current and new
                    # We label them as the leftover lines that are still missing
                    leftover_lines = self.find_common_elements(
                        list(current_missing_lines.values())[i],
                        list(new_missing_lines.values())[i],
                    )

                    # If we find that the leftover lines are fewer than the current missing lines
                    # That means we have fewer missing lines to cover
                    # That is interesting!
                    if len(leftover_lines) < len(list(current_missing_lines.values())[i]):
                        is_interesting_result = True
                        # Add the number of branch difference to our distance metric
                        distance += len(list(current_missing_lines.values())[i]) - len(leftover_lines)

                    # Assign the leftover lines to the file to be looked over the next coverage test
                    current_missing_lines[file] = leftover_lines

                    f = open(os.getcwd()+'/testdriver/missing_lines.json', 'w')
                    f.write(json.dumps(current_missing_lines))
                    f.close()
            elif mode == 'hash' and 'path_history' in current_missing_lines:
                
                # Get a Path ID as a hashed version of the missing lines object
                new_path_ID = hashlib.md5( json.dumps(new_missing_lines).encode() ).hexdigest()

                # Fetch the path history as a list of hashed path IDs
                path_history:list = current_missing_lines['path_history']
                
                if new_path_ID not in path_history:
                    # A new path!
                    is_interesting_result = True
                    path_history.append(new_path_ID)

                    # Update the output JSON file
                    f = open(os.getcwd()+'/testdriver/missing_lines.json', 'w')
                    f.write( json.dumps({
                        'path_history': path_history
                    }) )
                    f.close()
                    
                # Return the path ID regardless
                return_object = { 'hash': new_path_ID }
            else:
                logging.error('Invalid mode operation!')
        
        # If the missing lines json doesn't exist
        else:
            # By default consider the result interesting
            is_interesting_result = True

            # Begin storing the missing lines
            f = open(os.getcwd()+'/testdriver/missing_lines.json', 'w')

            if mode == 'distance':
                f.write( json.dumps(new_missing_lines) )
                return_object = { 'dist': totalno_missing_lines }
            else:
                # Get a Path ID as a hashed version of the missing lines object
                path_ID = hashlib.md5( json.dumps(new_missing_lines).encode() ).hexdigest()

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
        if os.path.exists(os.getcwd()+'/testdriver/missing_lines.json'):
            os.remove(os.getcwd()+'/testdriver/missing_lines.json')
        else:
            logging.error("The directory is already clean")

    def analyze_results(self, response):
        # Analyze the results of the server response
        pass
    
    def interpret(self, input_data):
        # interpret ASCII to fit to request
        
        return 0

# Usage
if __name__ == "__main__":

    # Configuration
    COAP_DIRECTORY = '../../CoAPthon/'

    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG)
    driver = CoapTestDriver(
        coap_dir=COAP_DIRECTORY
    )
    asyncio.run(driver.run_test())