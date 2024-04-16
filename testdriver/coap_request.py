from coapthon.messages.request import Request
from coapthon.client.helperclient import HelperClient
import logging


logger = logging.getLogger(__name__)

def test_case():
    
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
        with open("|COAP_DIR|/coap_fuzz.log", "w") as f:
            f.write(str(response))
            
    
                
    
    

if __name__ == "__main__":
    test_case()