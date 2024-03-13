import requests
import logging
import json

logging.basicConfig(level=logging.DEBUG)

class DjangoTestDriver:
    def __init__(self):
        self.server_url = "http://127.0.0.1:8000/"
        self.endpoints = ["api/product/", "datatb/product/add/", "datatb/product/edit/",
                "datatb/product/delete/", "datatb/product/export/", "accounts/register/", "accounts/login/"]

    # oracle to pass in the amount of test and list of inputs
    def run_fuzz_tests(self, num_tests, list_of_inputs):
        for i in range(num_tests):
            """
            When oracle passed in list of inputs 
             - response = await self.send_request(list_of_inputs[i])
             
            Note: Are we fuzzing endpoints or method?
            """
            
            # dummy
            response = self.send_request(list_of_inputs)
            logging.debug(response)
            self.analyze_results(response)
    
    def send_request(self, input_data):
        """
        Call interpret function to get readable inputs
         - input_data, headers = self.interpret(input_data)
        
        Note: Fuzzing Message code, uri, message type, payload, token, message id, options, version?
         - request = Message(code=input_data["code"], uri=input_data["url"], payload=input_data["payload"], mtype=input_data["mtype"], token=input_data["token"])
        """
        
        url = f"{self.server_url}{self.endpoints[1]}"
        
        ### example input
        input_data = {
            'name': "hello",
            'info': "bye",
            'price': 1
        }
        
        input_data = json.dumps(input_data)
        method = "get"
        headers = {}
        ################
        
        if method == "post":
            response = requests.post(url, data=input_data, headers=headers)
        elif method == "get":
            response = requests.get(url, data=input_data, headers=headers)
        elif method == "delete":
            response = requests.delete(url, data=input_data, headers=headers)
        elif method == "put":
            response = requests.put(url, data=input_data, headers=headers)
        
        logging.debug(response.__dict__)
        return response

    def analyze_results(self, response):
        # Analyze the results of the server response
        pass
    
    def interpret(self, input_data):
        # interpret ASCII to fit to request
        
        return 0

    
   
# Usage
if __name__ == "__main__":     
    driver = DjangoTestDriver()
    driver.run_fuzz_tests(2, [])