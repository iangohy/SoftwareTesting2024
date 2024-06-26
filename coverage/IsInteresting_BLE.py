from FuzzingCoverage import Coverage
import json, logging, os, hashlib

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

def parse_lcov_lines(lines:list[str]):
    count = 0
    array = [{}]
    totalno_missing_branches = 0
    output_dict = {}
    # Strips the newline character
    for line in lines:
        line = line.strip()
        splitline = line.split(":")
        if splitline[0] == "SF":
            array[count]["SF"] = splitline[1]
            array[count]["Branch"] = []

        if splitline[0] == "BRDA":
            if "Branch" in array[count].keys():
                brda = splitline[1].split(",")
                # If count is zero
                if brda[3] == "-" or 0:
                    totalno_missing_branches += 1
                    array[count]["Branch"].append([brda[0], brda[1]])
            else:
                array[count]["Branch"] = []
                brda = splitline[1].split(",")
                # If count is zero
                if brda[3] == "-" or 0:
                    totalno_missing_branches += 1
                    array[count]["Branch"].append([brda[0], brda[1]])
                
        if splitline[0] == "end_of_record":
            array.append({})
            count += 1

    for i in range(0, count):
        filename = array[i]['SF']
        branches = array[i]['Branch']
        output_dict.update({filename: branches})

    return output_dict, totalno_missing_branches

def is_interesting(mode:str = 'hash'):
    # Store the new missing branches from the report
    new_missing_branches = {}
    totalno_missing_branches = 0
    distance = 0

    # Opens the coverage JSON report
    try:
        f = open('lcov.info', 'r')
        lines = f.readlines()
        new_missing_branches, totalno_missing_branches = parse_lcov_lines(lines)
        f.close()
    except Exception:
        logging.error("Cannot open output file")

    is_interesting_result = False
    return_object = {}
    
    # If missing branches store file exists
    if os.path.exists(os.getcwd()+'/missing_branches.json'):

        # Open it and store the current missing branches
        try:
            f = open(os.getcwd()+'/missing_branches.json', 'r')
            current_missing_branches:dict = json.loads(f.read())
            f.close()
        except Exception:
            logging.error("Cannot open missing branch file")

        if mode == 'distance' and 'path_history' not in current_missing_branches:
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
                    # Add the number of branch difference to our distance metric
                    distance += len(list(current_missing_branches.values())[i]) - len(leftover_branches)

                # Assign the leftover branches to the file to be looked over the next coverage test
                current_missing_branches[file] = leftover_branches

                f = open(os.getcwd()+'/missing_branches.json', 'w')
                f.write(json.dumps(current_missing_branches))
                f.close()

                return_object = { 'dist': distance }
        elif mode == 'hash' and 'path_history' in current_missing_branches:
            # Get a Path ID as a hashed version of the missing branches object
            new_path_ID = hashlib.md5( json.dumps(new_missing_branches).encode() ).hexdigest()

            # Fetch the path history as a list of hashed path IDs
            path_history:list = current_missing_branches['path_history']
            
            if new_path_ID not in path_history:
                # A new path!
                is_interesting_result = True
                path_history.append(new_path_ID)

                # Update the output JSON file
                f = open(os.getcwd()+'/missing_branches.json', 'w')
                f.write( json.dumps({
                    'path_history': path_history
                }) )
                f.close()

            # Return the path ID regardless
            return_object = { 'hash': new_path_ID }
        else:
            logging.error('Invalid mode operation!')
    
    # If the missing branches json doesn't exist
    else:
        # By default consider the result interesting
        is_interesting_result = True

        # Begin storing the missing branches
        f = open(os.getcwd()+'/missing_branches.json', 'w')

        if mode == 'distance':
            f.write( json.dumps(new_missing_branches) )
            return_object = { 'dist': totalno_missing_branches }
        else:
            # Get a Path ID as a hashed version of the missing branches object
            path_ID = hashlib.md5( json.dumps(new_missing_branches).encode() ).hexdigest()

            # Start saving a history of paths checked
            f.write( json.dumps({
                'path_history':[ path_ID ]
            }) )

            return_object = { 'hash': path_ID }

        f.close()

    return (is_interesting_result, return_object)

def find_common_elements(list1, list2):
    return [element for element in list1 if element in list2]

if __name__ == "__main__":
    logging.info(is_interesting(mode='distance'))