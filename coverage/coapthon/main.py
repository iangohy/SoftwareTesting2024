import random, logging, os, json, asyncio, subprocess
from aiocoap import Context, Message, Code
logging.basicConfig(level=logging.DEBUG)

SERVER_URL = 'coap://127.0.0.1:5683'
COAPTHON_DIRECTORY = '../../../CoAPthon/'
COVERAGE_JSON_FILE = 'output.json'
MISSING_LINES_FILE = 'missing_lines.json'

async def send_request_with_coverage(endpoint, method, input:str):
    coverage_run = subprocess.Popen("coverage2 run --branch {}coapserver.py 127.0.0.1 -p 5683".format(COAPTHON_DIRECTORY), shell=True)

    url = "{}{}".format(SERVER_URL, endpoint)
    
    method_code = Code.GET
    if method == 'post':
        method_code = Code.POST
    elif method == 'put':
        method_code = Code.PUT
    elif method == 'patch':
        method_code = Code.PATCH
    elif method == 'delete':
        method_code = Code.DELETE

    request = Message(code=method_code, uri=url, payload=input.encode(), mtype=0, token=bytes("token",'UTF-8'))
    logging.debug(request.token)
    context = await Context.create_client_context()
    response = await context.request(request).response

    logging.info(response)

    coverage_run.terminate()

    json_report = subprocess.Popen("coverage2 json --pretty-print -o {}".format(COVERAGE_JSON_FILE), shell=True)

    logging.info("Coverage run complete for {}".format(input))

def is_interesting():
    # Opens the coverage JSON report
    f = open(COVERAGE_JSON_FILE, 'r')
    coverage_data = json.loads(f.read())
    f.close()

    is_interesting_result = False

    # Store the new missing lines from the report
    new_missing_lines = {}

    # Fetch the missing lines field from each file
    for file in coverage_data['files'].keys():
        if coverage_data['files'][file]['summary']['missing_lines'] <= 0:
            continue
        new_missing_lines[file] = coverage_data['files'][file]['missing_lines']

    # If missing lines store file exists
    if os.path.exists(MISSING_LINES_FILE):

        # Open it and store the current missing lines
        f = open(MISSING_LINES_FILE, 'r')
        current_missing_lines:dict = json.loads(f.read())
        f.close()

        # For each file index within the missing branch store
        for i in range(len(current_missing_lines.keys())):

            file = list(current_missing_lines.keys())[i]

            # Find the intersection / common lines between the current and new
            # We label them as the leftover lines that are still missing
            leftover_lines = find_common_elements(
                list(current_missing_lines.values())[i],
                list(new_missing_lines.values())[i],
            )

            # If we find that the leftover lines are fewer than the current missing lines
            # That means we have fewer missing lines to cover
            # That is interesting!
            if len(leftover_lines) < len(list(current_missing_lines.values())[i]):
                is_interesting_result = True

            # Assign the leftover lines to the file to be looked over the next coverage test
            current_missing_lines[file] = leftover_lines

            f = open(MISSING_LINES_FILE, 'w')
            f.write(json.dumps(current_missing_lines))
            f.close()
    
    # If the missing lines json doesn't exist
    else:
        # By default consider the result interesting
        is_interesting_result = True

        # Begin storing the missing lines
        f = open(MISSING_LINES_FILE, 'w')
        f.write(json.dumps(new_missing_lines))
        f.close()
    
    return is_interesting_result

def find_common_elements(list1, list2):
    return [element for element in list1 if element in list2]

def clean():
    if os.path.exists(MISSING_LINES_FILE):
        os.remove(MISSING_LINES_FILE)
    else:
        logging.error("The directory is already clean")

ENDPOINT = '/separate'
METHOD = 'post'
INPUT = "qwiojoidjqwaioji!"

if __name__ == "__main__":
    asyncio.run(send_request_with_coverage(ENDPOINT, METHOD, INPUT))
    logging.info("Is it interesting? {}".format(is_interesting()))