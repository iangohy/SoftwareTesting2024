import requests
import logging
import json
import os
import random

class DjangoTestDriver:
    def __init__(self, django_dir, test_template_file, test_output_file, coverage_json_file, missing_branches_file):
        self.server_url = "http://127.0.0.1:8000/"
        self.endpoints = ["api/product/", "datatb/product/add/", "datatb/product/edit/",
                "datatb/product/delete/", "datatb/product/export/", "accounts/register/", "accounts/login/"]
        self.django_dir = django_dir
        self.test_template_file = test_template_file
        self.test_output_file = test_output_file
        self.coverage_json_file = coverage_json_file
        self.missing_branches_file = missing_branches_file

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

        self.send_request_2(
            endpoint=self.endpoints[1],
            input_data={
                # Default fuzzing implementation
                'name': ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', k=10)),
                'info': ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', k=10)),
                'price': str(random.randint(1, 100)),
            },
            method='post',
            coverage=True
        )
    
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
            "ENDPOINT": '/'+endpoint,
            "NAME": input_data['name'],
            "INFO": input_data['info'],
            "PRICE": input_data['price'],
            "METHOD": method
        }

        # Reads the current template file
        f = open(self.test_template_file, 'r')
        data = f.read()
        f.close()

        # Replaces all keywords from text_to_replace
        for var in text_to_replace.keys():
            data = data.replace('|{}|'.format(var), text_to_replace[var])

        # Writes new TestCase for Django
        f = open(self.test_template_file, 'w')
        f.write(data)
        f.close()
    
        if coverage:
            # Runs the coverage command on the Django directory and generates a JSON report
            os.system("coverage3 run --branch --omit='tests.py' {}manage.py test; coverage3 json --pretty-print -o {}".format(self.django_dir, self.coverage_json_file))

            logging.info("Coverage run complete for {}".format(text_to_replace))

            logging.info("Is it interesting? {}".format(self.is_interesting()))
        else:
            # Runs the standard manage.py test command
            os.system("python3 {}manage.py test".format(self.django_dir))

            logging.info("Run complete for {}".format(text_to_replace))

    def analyze_results(self, response):
        # Analyze the results of the server response
        pass
    
    def interpret(self, input_data):
        # interpret ASCII to fit to request
        
        return 0
    
    def is_interesting(self):
        # Opens the coverage JSON report
        f = open(self.coverage_json_file, 'r')
        coverage_data = json.loads(f.read())
        f.close()

        is_interesting_result = False

        # Store the new missing branches from the report
        new_missing_branches = {}
        
        # Fetch the missing branches field from each file
        for file in coverage_data['files'].keys():
            if coverage_data['files'][file]['summary']['missing_branches'] <= 0:
                continue
            new_missing_branches[file] = coverage_data['files'][file]['missing_branches']

        # If missing branches store file exists
        if os.path.exists(self.missing_branches_file):

            # Open it and store the current missing branches
            f = open(self.missing_branches_file, 'r')
            current_missing_branches:dict = json.loads(f.read())
            f.close()

            # For each file index within the missing branch store
            for i in range(len(current_missing_branches.keys())):

                file = list(current_missing_branches.keys())[i]

                # Find the intersection / common branches between the current and new
                # We label them as the leftover branches that are still missing
                leftover_branches = self.find_common_elements(
                    list(current_missing_branches.values())[i],
                    list(new_missing_branches.values())[i],
                )

                # logging.debug(list(current_missing_branches.values())[i])
                # logging.debug(list(new_missing_branches.values())[i])
                # logging.debug(leftover_branches)

                # If we find that the leftover branches are fewer than the current missing branches
                # That means we have fewer missing branches to cover
                # That is interesting!
                if len(leftover_branches) < len(list(current_missing_branches.values())[i]):
                    is_interesting_result = True

                # Assign the leftover branches to the file to be looked over the next coverage test
                current_missing_branches[file] = leftover_branches

                f = open(self.missing_branches_file, 'w')
                f.write(json.dumps(current_missing_branches))
                f.close()
        
        # If the missing branches json doesn't exist
        else:
            # By default consider the result interesting
            is_interesting_result = True

            # Begin storing the missing branches
            f = open(self.missing_branches_file, 'w')
            f.write(json.dumps(new_missing_branches))
            f.close()

        return is_interesting_result

    def find_common_elements(self, list1, list2):
        return [element for element in list1 if element in list2]

    def clean(self):
        if os.path.exists(self.missing_branches_file):
            os.remove(self.missing_branches_file)
        else:
            logging.error("The directory is already clean")

# Usage
if __name__ == "__main__":  
    
    # Configuration
    DJANGO_DIRECTORY = '../../DjangoWebApplication/'
    TEST_TEMPLATE_FILE = 'template_test.py'
    TEST_OUTPUT_FILE = 'tests.py'
    COVERAGE_JSON_FILE = 'output.json'
    MISSING_BRANCHES_FILE = 'missing_branches.json'

    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG) 

    driver = DjangoTestDriver(
        django_dir=DJANGO_DIRECTORY,
        test_template_file=TEST_TEMPLATE_FILE,
        test_output_file=TEST_OUTPUT_FILE,
        coverage_json_file=COVERAGE_JSON_FILE,
        missing_branches_file=MISSING_BRANCHES_FILE
    )
    driver.run_test()