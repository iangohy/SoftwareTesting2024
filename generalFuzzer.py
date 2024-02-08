from coapthon.client.helperclient import HelperClient
import random
import string
import requests

class GeneralFuzzer:
    def __init__(self, type, host, port):
        self.host = host
        self.port = port
        self.client = HelperClient(server=(self.host, self.port))
        if type == 0:
            self.original_payload = "Hello, CoAP!"
        elif type == 1:
            self.original_payload = "Hello, Django!"        
        elif type == 2:
            self.original_payload = "Hello, Bluetooth!"


    def fuzz_payload(self, payload, num_bytes):
        # Generate random bytes to replace part of the payload
        fuzz_bytes = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(num_bytes))
        return payload[:3] + fuzz_bytes + payload[3 + num_bytes:]
    
    def fuzz_get_request(self, request):
        return 0
    
    def fuzz_post_request(self, request):
        return 0
    
    def fuzz_delete_request(self, request):
        return 0

    def fuzz_and_send_requests_coap(self, num_requests, num_bytes):
        for _ in range(num_requests):
            fuzzed_payload = self.fuzz_payload(self.original_payload, num_bytes)
            print("Fuzzing payload:", fuzzed_payload)

            # Send fuzzed GET request with the fuzzed payload and path "/basic/"
            response = self.client.get("/basic", payload=fuzzed_payload)
            print(response.pretty_print())
            
    def fuzz_and_send_requests_django(self, num_requests, num_bytes, endpoint):
        for _ in range(num_requests):
            fuzzed_payload = self.fuzz_payload(self.original_payload, num_bytes)
            print("Fuzzing payload:", fuzzed_payload)

            # Send fuzzed GET request with the fuzzed payload and path "/basic/"
            response = self.client.get(endpoint, payload=fuzzed_payload)
            print(response.pretty_print())
            
    def fuzz_and_send_requests_bluetooth(self, num_requests, num_bytes, endpoint):
        return 0

    def close_connection(self):
        self.client.stop()