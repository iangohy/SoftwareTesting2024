import requests
import random
import json
import threading
import time

def requestPost(url, headers, form_data):
    response = requests.post(url, headers=headers, data=form_data)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        print("Request successful!")
        print("Response:")
        print(response.status_code)
        # print(response)

    else:
        print(f"Request failed with status code: {response.__dict__}")


def requestGet(url, headers):
    response = requests.get(url, headers=headers)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        print("Request successful!")
        print("Response:")
        print(response._content)

    else:
        print(f"Request failed with status code: {response.__dict__}")
        print(
            f"Request failed with status code: {response.raw._original_response.__dict__}")


def requestDelete(url, headers):
    username="jiahui"
    passwd="123123"
    response = requests.delete(url, headers=headers, auth=(username, passwd))
    # response = requests.delete(url, headers=headers, auth=(username, passwd))

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        print("Request successful!")
        print("Response:")
        print(response.__dict__)

    else:
        print(f"Request failed with status code: {response.__dict__}")
        print(
            f"Request failed with status code: {response.raw._original_response.__dict__}")


def requestPut(url, headers, form_data):
    response = requests.put(url, headers=headers, data=json.dumps(form_data))

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        print("Request successful!")
        print("Response:")
        print(response.status_code)

    else:
        print(f"Request failed with status code: {response.__dict__}")
        print(
            f"Request failed with status code: {response.raw._original_response.__dict__}")


base_url = 'http://127.0.0.1:8000/'

endpoint_url = ["api/product/", "datatb/product/add/", "datatb/product/edit/",
                "datatb/product/delete/", "datatb/product/export/", "accounts/register/", "accounts/login/"]

# random_name = ''.join(random.choices(
#     'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', k=10))
# random_info = ''.join(random.choices(
#     'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', k=4))
# random_price = str(random.randint(1, 100))

# Define the headers with cookies
headers = {
    # 'Authorization': 'Token 5vvs6151ScRQGpdMlKAf8FAFERO67MmK',
    # 'X-CSRFToken': "5vvs6151ScRQGpdMlKAf8FAFERO67MmK",
    'Cookie': 'csrftoken=5vvs6151ScRQGpdMlKAf8FAFERO67MmK; sessionid=c35o5m7xkymbjdtcu9k916f8jfj2f8x7',  # Optional
}

try:

    threads = []

    # # create product
    # url = base_url + endpoint_url[1]
    # thread = threading.Thread(target=requestPost, args=(url, headers, json.dumps({
    #         'name': "yuXASaYiow",
    #         'info': "RbvE",
    #         'price': 1
    #     })
    # ))
    # thread.start()
    # threads.append(thread)
    
    # # create product
    # url = base_url + endpoint_url[1]
    # thread = threading.Thread(target=requestPost, args=(url, headers, json.dumps({
    #         'name': "pJFXbgwkon",
    #         'info': "Uoaq",
    #         'price': 2
    #     })
    # ))
    # thread.start()
    # threads.append(thread)
    
    # time.sleep(2)
    
    # # delete product
    # url = base_url + endpoint_url[3] + "1/" 
    # thread = threading.Thread(target=requestPost, args=(url, headers, {}))
    # thread.start()
    # threads.append(thread)
    
    # time.sleep(2)
    
    # # get products
    # url = base_url + endpoint_url[0]
    # thread = threading.Thread(target=requestGet, args=(url, headers))
    # thread.start()
    # threads.append(thread)
    
    # # edit products
    # url = base_url + endpoint_url[2] + "2/"
    # thread = threading.Thread(target=requestPost, args=(url, headers, json.dumps({"name": "hi"})))
    # thread.start()
    # threads.append(thread)
    
    # # edit products
    # url = base_url + endpoint_url[2] + "2/"
    # thread = threading.Thread(target=requestPut, args=(url, headers, {"name": "bye"}))
    # thread.start()
    # threads.append(thread)
    
    # # get products
    # url = base_url + endpoint_url[0] + "2/"
    # thread = threading.Thread(target=requestGet, args=(url, headers))
    # thread.start()
    # threads.append(thread)
    
    # delete products - doesnt work
    # url = base_url + endpoint_url[0] + "1/"
    # thread = threading.Thread(target=requestDelete, args=(url, headers))
    # thread.start()
    # threads.append(thread)
    
    # url = base_url + endpoint_url[6] 
    # credentials = {'username': 'jiahui', 'password': '123123'}

    # response = requests.post(url, data=credentials, headers=headers)
    
    # if response.status_code == 200:
    #     # can login but no session id or csrf_token
    #     print("Authentication successful")
    #     session_id = response.cookies.get('sessionid')
    #     print(response.__dict__)

    for thread in threads:
        thread.join()


except requests.exceptions.RequestException as e:
    print("Request failed:", e)


########### url to fuzz without auth ###########

# datatb/<str:model_name>/
# datatb/<str:model_name>/add/
# datatb/<str:model_name>/edit/<int:id>/
# datatb/<str:model_name>/delete/<int:id>/
# datatb/<str:model_name>/export/


########### url to fuzz with auth ###########
# api/product/pk