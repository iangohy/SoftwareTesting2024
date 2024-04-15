from aiocoap import Context, Message, Code
import asyncio

import logging


logger = logging.getLogger(__name__)

async def test_case():
    
    logger.info("In coap test")
    
    # if |COVERAGE|:
    #     await asyncio.create_subprocess_shell("coverage2 run --branch {}/coapserver.py 127.0.0.1 -p 5683".format("|COAP_DIR|"))
    # if not |COVERAGE|:
    #     await asyncio.create_subprocess_shell("python3 {}coapserver.py 127.0.0.1 -p 5683".format("|COAP_DIR|"))
        
    request = Message(code=|CODE|, uri="coap://127.0.0.1:5683|URL|", payload=b"|PAYLOAD|", mtype=0, token=bytes("token",'UTF-8'))
    context = await Context.create_client_context()
    response = await context.request(request).response

    logger.info(response)
    
    if response:
        with open("fuzz.log", "w") as f:
            f.write(str(response))
                
    
    

if __name__ == "__main__":
    asyncio.run(test_case())