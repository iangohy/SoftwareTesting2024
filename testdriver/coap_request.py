# -*- coding: utf-8 -*-
from coapthon.messages.request import Request
from coapthon.client.helperclient import HelperClient
import logging

logger = logging.getLogger(__name__)

def test_case():
    
    try:
        request = Request()
        request.code = |CODE|
        request.uri_path = "|URL|"
        request.payload = "|PAYLOAD|"
        request.destination = ("127.0.0.1", 5683)
        request.type = |TYPE|
        
        client = HelperClient(server=("127.0.0.1", 5683))

        response = client.send_request(request)
        
        logger.info(response)
        client.stop()
        
        if response:
            with open("coap_fuzz.log", "w") as f:
                f.write(str(response))
                
    except:
        logger.info("Error")
        
    

if __name__ == "__main__":
    test_case()