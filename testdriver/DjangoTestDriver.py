import requests
import logging

logging.basicConfig(level=logging.DEBUG)

class DjangoTestDriver:
    def __init__(self):
        self.server_url = "http://127.0.0.1:8000/"
        self.endpoints = ["api/product/", "datatb/product/add/", "datatb/product/edit/",
                "datatb/product/delete/", "datatb/product/export/", "accounts/register/", "accounts/login/"]

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
    
    def send_request(self, input_data, method):
        # Send a request to the server with the provided input data
        # choose from self.endpoints
        endpoint = self.endpoints[0] 
        url = f"{self.server_url}{endpoint}"
        # call interpret function to get readable inputs?
        input_data, headers = self.interpret(input_data)
        
        # example input
        input_data = {
            'name': "hello",
            'info': "bye",
            'price': 1
        }
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

    def run_fuzz_tests(self, num_tests):
        for _ in range(num_tests):
            structure = self.generate_random_structure()
            input_data = self.generate_random_input(structure)
            response = self.send_request(input_data, "get")
            self.analyze_results(response)
        
# Usage
driver = DjangoTestDriver()
driver.run_fuzz_tests(2)