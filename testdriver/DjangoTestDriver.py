import requests
import logging
import json
import os
import random

from smart_fuzzer.smartChunk import SmartChunk
logger = logging.getLogger(__name__)

class DjangoTestDriver:
    def __init__(self, django_dir):
        self.server_url = "http://127.0.0.1:8000/"
        self.endpoints = ["api/product/", "datatb/product/add/", "datatb/product/edit/",
                "datatb/product/delete/", "datatb/product/export/", "accounts/register/", "accounts/login/"]
        self.django_dir = django_dir

    # oracle to pass in the amount of test and list of inputs
    def run_test(self, chunk: SmartChunk, coverage: bool):
        logger.debug(f"Received chunk with content: {chunk.chunk_content}")
        chunk_endpoint = chunk.chunk_content

        self.send_request_with_interesting(
            endpoint=chunk_endpoint,
            input_data={
                # Default fuzzing implementation
                'name': ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', k=10)),
                'info': ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', k=10)),
                'price': str(random.randint(1, 100)),
            },
            method='post',
            coverage=coverage
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
        except Exception as ex:            
            logging.error(ex)
            
    
    def send_request_with_interesting(self, 
            # Default input config
            endpoint,
            input_data={'name': "hello",'info': "bye",'price': str(1)}, 
            method="get", # post | get | put | delete | patch
            coverage=False
        ):
        """
        Call interpret function to get readable inputs
         - input_data, headers = self.interpret(input_data)
        
        Note: Fuzzing formData and header
         - input_data["formData"] and input_data["headers"]
        """
        
        text_to_replace = {
            # endpoint should not need "/" in front
            "ENDPOINT": endpoint,
            "NAME": input_data['name'],
            "INFO": input_data['info'],
            "PRICE": input_data['price'],
            "METHOD": method
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
            os.system("coverage3 run --branch --omit='tests.py' {}manage.py test testdriver/; coverage3 json --pretty-print -o {}".format(self.django_dir, self.coverage_json_file))

            logging.info("Coverage run complete for {}".format(text_to_replace))

            logging.info("Is it interesting? {}".format(self.is_interesting()))
        else:
            # Runs the standard manage.py test command, look for tests in testdriver folder
            # os.system("python3 {}manage.py test testdriver/".format(self.django_dir))
            self.send_request(text_to_replace)

            logging.info("Run complete for {}".format(text_to_replace))

    def analyze_results(self, response):
        # Analyze the results of the server response
        pass
    
    def interpret(self, input_data):
        # interpret ASCII to fit to request
        
        return 0
    
    def is_interesting(self):
        # Opens the coverage JSON report
        try:
            f = open(os.getcwd()+'output.json', 'r')
            coverage_data = json.loads(f.read())
            f.close()
        except Exception:
            logging.error("Cannot open output file")

        is_interesting_result = False

        # Store the new missing branches from the report
        new_missing_branches = {}
        
        # Fetch the missing branches field from each file
        for file in coverage_data['files'].keys():
            if coverage_data['files'][file]['summary']['missing_branches'] <= 0:
                continue
            new_missing_branches[file] = coverage_data['files'][file]['missing_branches']

        # If missing branches store file exists
        if os.path.exists(os.getcwd()+'missing_branches.json'):

            # Open it and store the current missing branches
            try:
                f = open(os.getcwd()+'missing_branches.json', 'r')
                current_missing_branches:dict = json.loads(f.read())
                f.close()
            except Exception:
                logging.error("Cannot open missing branch file")

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

                # Assign the leftover branches to the file to be looked over the next coverage test
                current_missing_branches[file] = leftover_branches

                f = open(os.getcwd()+'missing_branches.json', 'w')
                f.write(json.dumps(current_missing_branches))
                f.close()
        
        # If the missing branches json doesn't exist
        else:
            # By default consider the result interesting
            is_interesting_result = True

            # Begin storing the missing branches
            f = open(os.getcwd()+'missing_branches.json', 'w')
            f.write(json.dumps(new_missing_branches))
            f.close()

        return is_interesting_result

    def find_common_elements(self, list1, list2):
        return [element for element in list1 if element in list2]

    def clean(self):
        if os.path.exists(os.getcwd()+'missing_branches.json'):
            os.remove(os.getcwd()+'missing_branches.json')
        else:
            logging.error("The directory is already clean")

# Usage
if __name__ == "__main__":  
    
    # Configuration
    DJANGO_DIRECTORY = '../../DjangoWebApplication/'

    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG) 

    driver = DjangoTestDriver(
        django_dir=DJANGO_DIRECTORY
    )
    driver.run_test()