from aiocoap import Context, Message, Code
import logging
import logging
import os
import json
import time
import signal
import hashlib
import configparser
from subprocess import Popen, PIPE, STDOUT, TimeoutExpired
from testdriver.utils import check_for_blacklist_phrase, sanitize_input, clean_gen_files
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
        clean_gen_files()
    
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
        # logger.info(f"payload: {str(payload):.50s}")
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
            "CODE":     sanitize_input(code),
            "URL":      sanitize_input(endpoint),
            "PAYLOAD":  sanitize_input(input_data),
            "TYPE":     "0"
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
        
        if os.path.exists(os.getcwd()+"/coap_fuzz.log"):
            os.remove(os.getcwd()+"/coap_fuzz.log")

        if coverage:            
            command = "coverage2 run {}/coapserver.py -i 127.0.0.1 -p 5683".format(self.coap_dir)
            logger.info(f"Running command: {command}")
            process_one = Popen(command, stdout=PIPE, stderr=STDOUT, text=True, shell=True, start_new_session=True)            
                
            command = f"python2 {self.coap_dir}/coap_test.py"
            logger.info(f"Running command: {command}")
            process_two = Popen(command, stdout=PIPE, stderr=STDOUT, text=True, shell=True, start_new_session=True)
            
            # WAIT FOR TEST CASE TO FINISH
            logger.info("Waiting for test file to complete")
            if test_number is not None:
                filename = f"{self.log_folderpath}/coap_testdriver_testfile_{test_number}.log"
            else:
                filename = f"{self.log_folderpath}/coap_testdriver_testfile_{int(time.time())}.log"
            with open(filename, "w") as file:
                    try:
                        self.process_stdout(process_two, file, 20)
                    except TestDriverCrashDetected:
                        # Force crash to end test file
                        pass
            logger.info("Test file completed")
            
            logger.info("Test file done, waiting for server to end.")
            os.killpg(os.getpgid(process_one.pid), signal.SIGINT) 

            try:
                if test_number is not None:
                    filename = f"{self.log_folderpath}/coap_testdriver_{test_number}.log"
                else:
                    filename = f"{self.log_folderpath}/coap_testdriver_{int(time.time())}.log"
                with open(filename, "w") as file:
                    self.process_stdout(process_one, file, 10)
            except TestDriverCrashDetected as e:
                if e.code != -2:
                    logger.exception(e)
                    logger.error(f"Test driver crashed while running test case: {input_data}")
                    # TODO: determine return values on crash
                    # Failure true
                    return (True, False, {})
            
            # WAIT FOR COAP SERVER TO END
            # process_one.wait()
            
            path_to_coverage = os.getcwd()+'/.coverage'

            is_interesting = False
            cov_data = {}
            response = None
            
            if os.path.exists(path_to_coverage):
                logging.debug("Coverage report found at: {}".format(path_to_coverage))
                command = "coverage2 json --pretty-print -o {}".format(os.getcwd()+'/testdriver/output.json')
                logger.debug(f"Running command: {command}")
                process_three = Popen(command, stdout=PIPE, stderr=STDOUT, text=True, shell=True, start_new_session=True)
                
                # WAIT FOR COVERAGE OUTPUT TO FINISH
                process_three.wait()

                try:
                    is_interesting, cov_data = self.is_interesting(mode)
                except Exception as e:
                    # Failure true
                    return (True, False, {})
                # logging.info("Coverage run complete for {:.100}".format(str(text_to_replace)))
                logging.info("Coverage run complete for {}".format(str(text_to_replace)))
                logging.info("Is it interesting? {}".format(is_interesting))
            
                try:
                    with open("coap_fuzz.log", "r") as f:
                        response = {"status_code": f.readline()}
                except FileNotFoundError:
                    logger.info("File not Found")
                    # Error occurred running test case
                    return (False, False, {})
                response.update(cov_data)

            else:
                logging.error("Coverage output not found!")
            
            return (False, is_interesting, response)

    def process_stdout(self, process: Popen, logfile, timeout=10):
        logger.info("Handling target application stdout and stderr")
        # Case ignored
        blacklist = ["segmentation fault", "core dumped"]
        logger.debug(f"Blacklist is: {blacklist}")

        start_time = time.time()
        timeout = start_time + timeout

        while time.time() < timeout:
            os.set_blocking(process.stdout.fileno(), False)
            try:
                stdout_data = process.stdout.readline()
            except UnicodeDecodeError as e:
                logger.exception(e)
                continue
            if stdout_data:
                logger.debug(f"stdout_data: {stdout_data}")
                if logfile:
                    logfile.write(stdout_data)
                    check_for_blacklist_phrase(stdout_data, blacklist)
            if process.poll() is not None:
                return        
        process.kill()
        raise TestDriverCrashDetected("CoAP server not responding to SIGNINT after 10s")

        # while True:
        #     # if self.exit_event.is_set():
        #     #     raise KeyboardInterrupt()
        #     os.set_blocking(process.stdout.fileno(), False)
        #     # line = non_block_read(process.stdout)
        #     try:
        #         while True:
        #             line = process.stdout.readline()
        #             if line:
        #                 logger.debug(f"OUTPUT: {line}")
        #                 if logfile:
        #                     logfile.write(line)
        #                 check_for_blacklist_phrase(line, blacklist)
        #             else:
        #                 break
        #     except:
        #         logger.error("Unable to parse stdout")
        #         if logfile:
        #                 logfile.write("Unable to parse stdout")
        #     if process.poll() is not None:
        #         break

        # status = process.poll()
        # if status != 0:
        #     raise TestDriverCrashDetected(f"Process exited with signal {process.poll()}", process.poll())
        # else:
        #     logger.debug("Process exited with status 0")
            
    def is_interesting(self, mode:str = 'hash'):
        # Opens the coverage JSON report
        try:
            f = open(os.getcwd()+'/testdriver/output.json', 'r')
            coverage_data = json.loads(f.read())
            f.close()
        except Exception as e:
            logging.error("Cannot open output file: {}".format(e))

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
                # If it finds that the number of files with missing branches is less than the current number
                # That means we have fewer missing branches to cover
                # That is interesting!
                if len(new_missing_lines.keys()) < len(current_missing_lines.keys()):
                    is_interesting_result = True

                # For each file index within the missing branch store
                for i in range( min( len(current_missing_lines.keys()), len(new_missing_lines.keys()) ) ):

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

                    return_object = { 'dist': distance }

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

    def analyze_results(self, response):
        # Analyze the results of the server response
        pass
    
    def interpret(self, input_data):
        # interpret ASCII to fit to request
        
        return 0

# Usage
if __name__ == "__main__":
    # Mock config
    config = configparser.ConfigParser()
    config['DEFAULT'] = {'coap_dir':  '../../CoAPthon/',
                     'Compression': 'yes',
                     'CompressionLevel': '9'}

    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG)
    driver = CoapTestDriver(config["DEFAULT"], "logs")

    # Mock SChunk
    endpoint_schunk = SChunk("endpoint", chunk_content="basic")
    payload_schunk = SChunk("payload", chunk_content="lolololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololololoe")
    code_schunk = SChunk("code", chunk_content="1")
    root_schunk = SChunk("root", children={endpoint_schunk, payload_schunk, code_schunk},
                         lookup_chunks={"endpoint": endpoint_schunk, "payload": payload_schunk, "code": code_schunk})
    driver.run_test(root_schunk, True, 9999)