from aiocoap import Context, Message, Code

import asyncio
import logging

logging.basicConfig(level=logging.DEBUG)

class CoapTestDriver:
    def __init__(self):
        self.server_url = "coap://127.0.0.1:5683"
        self.endpoints = ['/basic', '/storage', '/child', '/separate', '/etag', '/', '/big', '/encoding', '/advancedSeparate', '/void', '/advanced', '/long', '/xml']
    
    # oracle to pass in the amount of test and list of inputs
    async def run_fuzz_tests(self, num_tests, list_of_inputs):
        for i in range(num_tests):
            """
            When oracle passed in list of inputs 
             - response = await self.send_request(list_of_inputs[i])
             
            Note: Are we fuzzing endpoints?
            """
            
            # dummy
            response = await self.send_request(list_of_inputs)
            logging.debug(response)
            self.analyze_results(response)
    
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

    def analyze_results(self, response):
        # Analyze the results of the server response
        pass
    
    def interpret(self, input_data):
        # interpret ASCII to fit to request
        
        return 0

    
        
    
# Usage
if __name__ == "__main__":
    driver = CoapTestDriver()
    asyncio.run(driver.run_fuzz_tests(2, []))