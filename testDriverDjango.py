import requests
import random
import json
import threading

def requestPost(url, headers, form_data):
    response = requests.post(url, headers=headers, data=json.dumps(form_data))
    
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        print("Request successful!")
        print("Response:")
        print(response.__dict__)

    else:
        print(f"Request failed with status code: {response.__dict__}")
        print(f"Request failed with status code: {response.raw._original_response.__dict__}")

def requestGet(url, headers):
    response = requests.get(url, headers=headers)
    
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        print("Request successful!")
        print("Response:")
        print(response.__dict__)

    else:
        print(f"Request failed with status code: {response.__dict__}")
        print(f"Request failed with status code: {response.raw._original_response.__dict__}")


def requestDelete(url, headers):
    response = requests.delete(url, headers=headers)
    
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        print("Request successful!")
        print("Response:")
        print(response.__dict__)

    else:
        print(f"Request failed with status code: {response.__dict__}")
        print(f"Request failed with status code: {response.raw._original_response.__dict__}")

def requestPut(url, headers, form_data):
    response = requests.put(url, headers=headers, data=json.dumps(form_data))
    
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        print("Request successful!")
        print("Response:")
        print(response.status_code)

    else:
        print(f"Request failed with status code: {response.__dict__}")
        print(f"Request failed with status code: {response.raw._original_response.__dict__}")




base_url = 'http://127.0.0.1:8000/'

endpoint_url = ["api/product/", "datatb/product/add/", "datatb/product/edit/1", "datatb/product/delete/1", "datatb/product/export"]


random_name = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', k=10))
random_info = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', k=4))
random_price = str(random.randint(1, 100))

form_data = {
    'name': random_name,
    'info': random_info,
    'price': 1
}

# Define the headers with cookies
headers = {
    'Cookie': 'csrftoken=5vvs6151ScRQGpdMlKAf8FAFERO67MmK; sessionid=c35o5m7xkymbjdtcu9k916f8jfj2f8x7', # Optional
}

try:
    print(json.dumps(form_data))
    # response = requests.post(url, headers=headers, data=json.dumps(form_data))
    
    threads = []
    
    url = base_url + endpoint_url[1]
    for i in range(1):
        thread = threading.Thread(target=requestPost, args=(url, headers, form_data))
        thread.start()
        threads.append(thread)
    
    url = base_url + endpoint_url[0]    
    for i in range(1):
        thread = threading.Thread(target=requestGet, args=(url, headers))
        thread.start()
        threads.append(thread)
        
    for thread in threads:
        thread.join()
    

    
except requests.exceptions.RequestException as e:
    print("Request failed:", e)




########### url to fuzz ###########

# datatb/<str:model_name>/
# datatb/<str:model_name>/add/
# datatb/<str:model_name>/edit/<int:id>/
# datatb/<str:model_name>/delete/<int:id>/
# datatb/<str:model_name>/export/