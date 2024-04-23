import random, logging, os, json

TEST_TEMPLATE_FILE = 'template_test.py'
TEST_OUTPUT_FILE = 'tests.py'
DJANGO_DIRECTORY = '../../../DjangoWebApplication/'
COVERAGE_JSON_FILE = 'output.json'
MISSING_BRANCHES_FILE = 'missing_branches.json'

def send_request_with_coverage(text_to_replace):
    # Reads the current template file
    f = open(TEST_TEMPLATE_FILE, 'r')
    data = f.read()
    f.close()

    # Replaces all keywords from text_to_replace
    for var in text_to_replace.keys():
        data = data.replace('|{}|'.format(var), text_to_replace[var])

    # Writes new TestCase for Django
    f = open(TEST_OUTPUT_FILE, 'w')
    f.write(data)
    f.close()
    
    # Runs the coverage command on the Django directory and generates a JSON report
    os.system("coverage3 run --branch --omit='tests.py' {}manage.py test; coverage3 json -o {}".format(DJANGO_DIRECTORY, COVERAGE_JSON_FILE))

    logging.info("Coverage run complete for {:.100}".format(str(text_to_replace)))

def is_interesting():
    # Opens the coverage JSON report
    f = open(COVERAGE_JSON_FILE, 'r')
    coverage_data = json.loads(f.read())
    f.close()

    is_interesting_result = False

    # Store the new missing branches from the report
    new_missing_branches = {}
    
    # Fetch the missing branches field from each file
    for file in coverage_data['files'].keys():
        if coverage_data['files'][file]['summary']['missing_branches'] <= 0:
            continue
        new_missing_branches[file] = coverage_data['files'][file]['missing_branches']

    # If missing branches store file exists
    if os.path.exists(MISSING_BRANCHES_FILE):

        # Open it and store the current missing branches
        f = open(MISSING_BRANCHES_FILE, 'r')
        current_missing_branches:dict = json.loads(f.read())
        f.close()

        # For each file index within the missing branch store
        for i in range(len(current_missing_branches.keys())):

            file = list(current_missing_branches.keys())[i]

            # Find the intersection / common branches between the current and new
            # We label them as the leftover branches that are still missing
            leftover_branches = find_common_elements(
                list(current_missing_branches.values())[i],
                list(new_missing_branches.values())[i],
            )

            # If we find that the leftover branches are fewer than the current missing branches
            # That means we have fewer missing branches to cover
            # That is interesting!
            if len(leftover_branches) < len(list(current_missing_branches.values())[i]):
                is_interesting_result = True

            # Assign the leftover branches to the file to be looked over the next coverage test
            current_missing_branches[file] = leftover_branches

            f = open(MISSING_BRANCHES_FILE, 'w')
            f.write(json.dumps(current_missing_branches))
            f.close()
    
    # If the missing branches json doesn't exist
    else:
        # By default consider the result interesting
        is_interesting_result = True

        # Begin storing the missing branches
        f = open(MISSING_BRANCHES_FILE, 'w')
        f.write(json.dumps(new_missing_branches))
        f.close()

    return is_interesting_result

def find_common_elements(list1, list2):
    return [element for element in list1 if element in list2]

def clean():
    if os.path.exists(MISSING_BRANCHES_FILE):
        os.remove(MISSING_BRANCHES_FILE)
    else:
        logging.error("The directory is already clean")

if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG)

    # Default Fuzzing Implementation. To be replaced by external fuzzer.
    text_to_replace = {
        "ENDPOINT": "/datatb/product/add/",
        "NAME": ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', k=10)),
        "INFO": ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', k=2)),
        "PRICE": str(random.randint(1, 100)),
        "METHOD": "post" # post | get | put | delete | patch
    }

    send_request_with_coverage(text_to_replace)
    logging.info("Is it interesting? {}".format(is_interesting()))