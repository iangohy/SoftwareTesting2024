from coapthon.messages.request import Request
from coapthon.client.helperclient import HelperClient

import logging


logger = logging.getLogger(__name__)

def test_case():
    
    logger.info("In coap test")
    
    # if True:
    #     await asyncio.create_subprocess_shell("coverage2 run --branch {}/coapserver.py 127.0.0.1 -p 5683".format("SoftwareTestingRepo/CoAPthon"))
    # if not True:
    #     await asyncio.create_subprocess_shell("python3 {}coapserver.py 127.0.0.1 -p 5683".format("SoftwareTestingRepo/CoAPthon"))
        
    request = Request()
    request.code = |CODE|
    request.uri_path = "|URL|"
    request.payload = "|PAYLOAD|"
    
    client = HelperClient("|ADDRESS|")

    response = client.send_request(request)

    logger.info(response)
    
    if response:
        with open("fuzz.log", "w") as f:
            f.write(str(response))
                
    
    

if __name__ == "__main__":
    test_case()