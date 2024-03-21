from django.test import TestCase
from django.urls import reverse

import logging
import json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class CoverageTests(TestCase):
    def test_client(self):
        # endpoint = "/api/product/add/" - should be just a uri
        endpoint = "/http://127.0.0.1:8000/api/delete/"
        method = "post"
        
        # form_data = {
        #     'name': "sdsds",
        #     'info': "wW",
        #     'price': 73
        # }
        
        form_data = {
            'name': "RDnJaCwLQA",
            'info': "HGYqRKEJJq",
            'price': "67" # should be integer
        }
        
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
        
        logging.info("Response \t%s",response.status_code)
        
        # self.assertEqual(response.status_code, 200)
        # self.assertNotIn(b'ValueError', response)