from aiocoap import Context, Message, Code

import asyncio
import logging

logging.basicConfig(level=logging.DEBUG)

class CoapTestDriver:
    def __init__(self):
        self.server_url = "coap://127.0.0.1:5683"
        self.endpoints = ['/basic', '/storage', '/child', '/separate', '/etag', '/', '/big', '/encoding', '/advancedSeparate', '/void', '/advanced', '/long', '/xml']
        

    def generate_random_structure(self):
        # generate_random_structure
        pass

    def generate_random_input(self, structure):
        # generate_random_input based on structure
        # should return test case as a whole in ASCII
        pass
    
    def interpret(self, input_data):
        # interpret ASCII to fit to request
        
        return "", ""
    
    async def send_request(self, input_data):
        # Send a request to the server with the provided input data
        # choose from self.endpoints
        endpoint = "/your_endpoint" 
        url = f"{self.server_url}{endpoint}"
        # call interpret function to get readable inputs?
        input_data, headers = self.interpret(input_data)
        
        # example
        request = Message(code=Code.GET, uri=url, payload=input_data, mtype=0, token=bytes("token",'UTF-8'))
        logging.debug(request.token)
        context = await Context.create_client_context()
        response = await context.request(request).response
        
        return response

    def analyze_results(self, response):
        # Analyze the results of the server response
        pass

    async def run_fuzz_tests(self, num_tests):
        for _ in range(num_tests):
            structure = self.generate_random_structure()
            input_data = self.generate_random_input(structure)
            response = await self.send_request(input_data)
            logging.debug(response)
            self.analyze_results(response)
        
    
# Usage
driver = CoapTestDriver()
asyncio.run(driver.run_fuzz_tests(2))