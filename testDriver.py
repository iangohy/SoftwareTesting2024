

from coapthon.client.helperclient import HelperClient
from request import Request
import string
import random
from multiprocessing import Process
import threading
import time


# Please put this file in Coapthon folder

def readInputFileAsRequest(filePath, target):
    inputDictionary = {}
    req = Request()
    
    if target == 0:
        # Type (T): 2-bit unsigned integer. 
        # Token Length (TKL): 4-bit unsigned integer. 
        # Code:  8-bit unsigned integer 
        # Message ID is a 16-bit identifier in CoAP messages
        # Token: 0 to 8 bytes
        
        with open("./"+filePath, 'r') as file:
            # Read and print each line
            for line in file:
                line = line.strip()
                line = line.split(":")
                # print(line[1])
                inputDictionary[line[0]] = line[1]
        
        # print(inputDictionary)
        req.type = int(inputDictionary["type"])
        req.code = int( inputDictionary["code"])
        req.mid = int(inputDictionary["mid"])
        req.uri_path = inputDictionary["mid"]
        req.token = inputDictionary["uri_path"]
        setattr(req, "payload", "hi")
    
    
    return req
    # This can include modifying the length, content type, or structure of the payload.
    
def client_function(request, timeout):
    # Simulate client activities
    host = "127.0.0.1"
    port = 5683
    client = HelperClient(server=(host, port))
    request.destination = client.server

    client.send_request(request, timeout)
    

    
def testDriver():
    # req = readInputFileAsRequest("test-coap.txt", 0)
    paths = ['/basic', '/storage', '/child', '/separate', '/etag', '/', '/big', '/encoding', '/advancedSeparate', '/void', '/advanced', '/long', '/xml']
    threads = []
    
    req2 = Request()
    req2.type = 0 # confirmable
    req2.code = 1 # get 
    req2.mid = 16001
    req2.uri_path = paths[0]
    req2.observe = 0 # observe 
    req2.token =  ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(2))
    print(req2)
    
    thread = threading.Thread(target=client_function, args=((req2, 1)))
    thread.start()
    threads.append(thread)
    
    time.sleep(5)
    
    req = Request()
    req.type = 0 # confirmable
    req.code = 3 # put 
    req.mid = 16002
    req.uri_path = paths[0]
    req.token =  ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(2))
    setattr(req, "payload", "byebye")
    print(req)
    
    thread = threading.Thread(target=client_function, args=(req,1))
    thread.start()
    threads.append(thread)
    
    
    time.sleep(5)
    
    
    setattr(req, "payload", "hi")
    req.token =  ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(2))
    req.mid = 16003
    
    thread = threading.Thread(target=client_function, args=(req,1))
    thread.start()
    threads.append(thread)
    
    for thread in threads:
        thread.join()
    
    
    
    

if __name__ == "__main__":
    testDriver()
    

############ put request for /basic ############
# req = Request()
# req.type = 0 # confirmable
# req.code = 3 # put 
# req.mid = 16002
# req.uri_path = paths[0]
# req.token =  ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(2))
# req.destination = client.server
# setattr(req, "payload", "byebye")
    
# print(req)
# response = client.send_request(req, timeout=1)
    
############ get request for /basic, response should return byebye instead of Basic Resource ############
# req2 = Request()
# req2.type = 0 # confirmable
# req2.code = 1 # get 
# req2.mid = 16001
# req2.uri_path = paths[0]
# req2.token =  ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(2))
# req2.destination = client.server

# print(req2)
# client.send_request(req2, timeout=1)
    
    
############ other attributes to edit ############
# req.accept - content type
    # "text/plain": 0,
    # "application/link-format": 40,
    # "application/xml": 41,
    # "application/octet-stream": 42,
    # "application/exi": 47,
    # "application/json": 50
# req.if_match(listofvalues) - if the server store content matches with value, then update content with payload
    
    
# for i in range(len(paths)):
#     req = Request()
#     req.type = 0 # confirmable
#     req.code = 3 # put
#     req.mid = 16002
#     req.uri_path = paths[i]
#     req.token = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(2))
#     tokens.append(req.token)
#     req.destination = client.server
#     setattr(req, "payload", "byebye")
#     print(req)
#     response = client.send_request(req, timeout=1)
    
# for i in range(len(paths)):
#     req = Request()
#     req.type = 0 # confirmable
#     req.accept(0) # "text/plain"
#     req.code = 1 # get 
#     req.mid = 16002
#     req.uri_path = paths[i]
#     req.token =  ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(2))
#     req.destination = client.server
#     print(req)
#     response = client.send_request(req, timeout=1)
        

