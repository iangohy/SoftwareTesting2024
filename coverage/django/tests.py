import requests,random,json,logging

from django.test import TestCase, Client

logging.basicConfig(level=logging.INFO)

# coverage run --branch manage.py test [--keepdb]; coverage report > output.txt
# coverage run --branch manage.py test; coverage json -o output.json

class CoverageTests(TestCase):
    def test_client(self):
        c = Client()
        endpoint = "/datatb/product/add/"

        form_data = {
            'name': "jyqdobdeYl",
            'info': "Dp",
            'price': "89"
        }
        logging.info("Input \t%s",form_data)

        method = "get"

        if method == "post":
            response = c.post(endpoint, form_data, content_type='application/json')
        elif method == "delete":
            response = c.delete(endpoint, form_data, content_type='application/json')
        elif method == "put":
            response = c.put(endpoint, form_data, content_type='application/json')
        elif method == "patch":
            response = c.patch(endpoint, form_data, content_type='application/json')
        else:
            response = c.get(endpoint, form_data, content_type='application/json')
        
        logging.info("Response \t%s",response.content.decode('utf-8'))