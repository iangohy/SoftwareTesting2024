import requests
import random
import json
import threading
import asyncio
from aiocoap import Context, Message, Code

base_url = 'coap://127.0.0.1:5683/basic'

async def coap_request():

    # Create a CoAP context
    context = await Context.create_client_context()

    # Create a CoAP request message
    request = Message(code=Code.GET, uri=base_url)
    print(request.__dict__)

    try:
        # Send the request and wait for the response
        response = await context.request(request).response

        # Print the response payload
        print(f"Response: {response.payload.decode('utf-8')}")

    except Exception as e:
        print(f"Error: {e}")

# Run the CoAP request asynchronously
asyncio.run(coap_request())

########### url to fuzz ###########

# datatb/<str:model_name>/
# datatb/<str:model_name>/add/
# datatb/<str:model_name>/edit/<int:id>/
# datatb/<str:model_name>/delete/<int:id>/
# datatb/<str:model_name>/export/