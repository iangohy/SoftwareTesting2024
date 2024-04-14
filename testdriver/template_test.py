from django.test import TestCase
from django.urls import reverse

import logging
import json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class CoverageTests(TestCase):
    def test_client(self):
        # endpoint = "/api/product/add/" - should be just a uri
        
        endpoint = "/|ENDPOINT|"
        method = "|METHOD|"
        
        # form_data = {
        #     'name': "sdsds",
        #     'info': "wW",
        #     'price': 73
        # }
        
        form_data = "|FORM_DATA|"
        
        logging.info("========Starting request========")
        
        if method == "post":
            response = self.client.post(endpoint, form_data, content_type='application/json')
        elif method == "delete":
            response = self.client.delete(endpoint, form_data, content_type='application/json')
        elif method == "put":
            response = self.client.put(endpoint, form_data, content_type='application/json')
        elif method == "patch":
            response = self.client.patch(endpoint, form_data, content_type='application/json')
        else:
            response = self.client.get(endpoint)
        
        if response:
            with open("fuzz.log", "w") as f:
                f.write(str(response.status_code))
                
        else:
            with open("fuzz.log", "w") as f:
                f.write("No connection adapters")
                
        logging.info("========Ending request========")
        # logging.info("Response \t%s",response.status_code)