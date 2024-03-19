import requests
import logging
import json
import os

logging.basicConfig(level=logging.DEBUG)

# Configuration
DJANGO_DIRECTORY = '../../DjangoWebApplication/'
TEST_TEMPLATE_FILE = 'template_test.py'
TEST_OUTPUT_FILE = 'tests.py'
COVERAGE_JSON_FILE = 'output.json'
MISSING_BRANCHES_FILE = 'missing_branches.json'

class DjangoTestDriver:
    def __init__(self):
        self.server_url = "http://127.0.0.1:8000/"
        self.endpoints = ["api/product/", "datatb/product/add/", "datatb/product/edit/",
                "datatb/product/delete/", "datatb/product/export/", "accounts/register/", "accounts/login/"]

    # oracle to pass in the amount of test and list of inputs
    def run_test(self, list_of_inputs=[]):
        """
        When oracle passed in list of inputs 
            - response = await self.send_request(list_of_inputs[i])
            
        Note: Are we fuzzing endpoints or method?
        """
        
        # dummy
        # response = self.send_request(list_of_inputs)
        # logging.debug(response)
        # self.analyze_results(response)

        self.send_request_2(endpoint=self.endpoints[1], coverage=False)
    
    def send_request(self, input_data):
        """
        Call interpret function to get readable inputs
         - input_data, headers = self.interpret(input_data)
        
        Note: Fuzzing formData and header
         - input_data["formData"] and input_data["headers"]
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
    
    def send_request_2(self, 
            endpoint,
            input_data={'name': "hello",'info': "bye",'price': str(1)}, 
            method="post", # post | get | put | delete | patch
            coverage=False
        ):
        """
        Call interpret function to get readable inputs
         - input_data, headers = self.interpret(input_data)
        
        Note: Fuzzing formData and header
         - input_data["formData"] and input_data["headers"]
        """
        
        text_to_replace = {
            "ENDPOINT": '/'+endpoint,
            "NAME": input_data['name'],
            "INFO": input_data['info'],
            "PRICE": input_data['price'],
            "METHOD": method
        }

        # Reads the current template file
        f = open(TEST_TEMPLATE_FILE, 'r')
        data = f.read()
        f.close()

        # Replaces all keywords from text_to_replace
        for var in text_to_replace.keys():
            data = data.replace('|{}|'.format(var), text_to_replace[var])

        # Writes new TestCase for Django
        f = open(TEST_OUTPUT_FILE, 'w')
        f.write(data)
        f.close()
    
        if coverage:
            # Runs the coverage command on the Django directory and generates a JSON report
            os.system("coverage3 run --branch --omit='tests.py' {}manage.py test; coverage3 json --pretty-print -o {}".format(DJANGO_DIRECTORY, COVERAGE_JSON_FILE))

            logging.info("Coverage run complete for {}".format(text_to_replace))
        else:
            # Runs the standard manage.py test command
            os.system("python3 {}manage.py test".format(DJANGO_DIRECTORY))

            logging.info("Run complete for {}".format(text_to_replace))

    def analyze_results(self, response):
        # Analyze the results of the server response
        pass
    
    def interpret(self, input_data):
        # interpret ASCII to fit to request
        
        return 0

# Usage
if __name__ == "__main__":     
    driver = DjangoTestDriver()
    driver.run_test()