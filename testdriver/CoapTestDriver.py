from aiocoap import Context, Message, Code
import random
import asyncio
import logging
import os
import json
from smart_fuzzer.smartChunk import SmartChunk

class CoapTestDriver:
    def __init__(self, coap_dir):
        self.server_url = "coap://127.0.0.1:5683"
        self.endpoints = ['/basic', '/storage', '/child', '/separate', '/etag', '/', '/big', '/encoding', '/advancedSeparate', '/void', '/advanced', '/long', '/xml']
        self.coap_dir = coap_dir
    
    # oracle to pass in 
    async def run_test(self, chunk: SmartChunk, coverage: bool):
        """
        When oracle passed in list of inputs 
            - response = await self.send_request(list_of_inputs[i])
        """
        logger.debug(f"Received chunk with content: {chunk.chunk_content}")
        chunk_endpoint = chunk.chunk_content
        
        self.send_request_with_interesting(
            endpoint=chunk_endpoint,
            # Default fuzzing implementation
            input_data=''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', k=10)),
            method='post',
            coverage=coverage
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
    
    async def send_request_with_interesting(self,
            # Default input config
            endpoint, 
            method = "post", 
            input_data:str = 'Hello world!',
            coverage=False
        ):
        url = "{}{}".format(self.server_url, endpoint)
        
        method_code = Code.GET
        if method == 'post':
            method_code = Code.POST
        elif method == 'put':
            method_code = Code.PUT
        elif method == 'patch':
            method_code = Code.PATCH
        elif method == 'delete':
            method_code = Code.DELETE

        if coverage:
            coverage_run = await asyncio.create_subprocess_shell("coverage2 run --branch {}coapserver.py 127.0.0.1 -p 5683".format(self.coap_dir))

            request = Message(code=method_code, uri=url, payload=input_data.encode(), mtype=0, token=bytes("token",'UTF-8'))
            logging.debug(request.token)
            context = await Context.create_client_context()
            response = await context.request(request).response

            logging.info(response)

            coverage_run.terminate()

            json_report = await asyncio.create_subprocess_shell("coverage2 json --pretty-print -o {}".format(os.getcwd()+'/testdriver/output.json'))
            await json_report.wait()

            logging.info("Coverage run complete for {}".format(input_data))

            logging.info("Is it interesting? {}".format(self.is_interesting()))
        else:
            # normal_run = await asyncio.create_subprocess_shell("python3 {}coapserver.py 127.0.0.1 -p 5683".format(self.coap_dir))
            request = Message(code=method_code, uri=url, payload=input_data.encode(), mtype=0, token=bytes("token",'UTF-8'))
            logging.debug(request.token)
            context = await Context.create_client_context()
            response = await context.request(request).response

            logging.info(response)

            logging.info("Run complete for {}".format(input_data))

    def is_interesting(self):
        # Opens the coverage JSON report
        try:
            f = open(os.getcwd()+'/testdriver/output.json', 'r')
            coverage_data = json.loads(f.read())
            f.close()
        except Exception:
            logging.error("Cannot open output file")

        is_interesting_result = False

        # Store the new missing lines from the report
        new_missing_lines = {}

        # Fetch the missing lines field from each file
        for file in coverage_data['files'].keys():
            if coverage_data['files'][file]['summary']['missing_lines'] <= 0:
                continue
            new_missing_lines[file] = coverage_data['files'][file]['missing_lines']

        # If missing lines store file exists
        if os.path.exists(os.getcwd()+'/testdriver/missing_lines.json'):

            # Open it and store the current missing lines
            try:
                f = open(os.getcwd()+'/testdriver/missing_lines.json', 'r')
                current_missing_lines:dict = json.loads(f.read())
                f.close()
            except Exception:
                logging.error("Cannot open missing lines file")
            
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

                # Assign the leftover lines to the file to be looked over the next coverage test
                current_missing_lines[file] = leftover_lines

                f = open(os.getcwd()+'/testdriver/missing_lines.json', 'w')
                f.write(json.dumps(current_missing_lines))
                f.close()
        
        # If the missing lines json doesn't exist
        else:
            # By default consider the result interesting
            is_interesting_result = True

            # Begin storing the missing lines
            f = open(os.getcwd()+'/testdriver/missing_lines.json', 'w')
            f.write(json.dumps(new_missing_lines))
            f.close()
        
        return is_interesting_result

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