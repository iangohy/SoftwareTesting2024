import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

file1 = open('lcov.info', 'r')
Lines = file1.readlines()
 
count = 0
array = [{}]
dict = {}
# Strips the newline character
for line in Lines:
    line = line.strip()
    splitline = line.split(":")
    if splitline[0] == "SF":
        array[count]["SF"] = splitline[1]
        array[count]["Branch"] = []
        
    # if splitline[0] == "DA":
    #     linehitsplit = splitline[1].split(",")
    #     if linehitsplit[1] == "0":
    #         if "LineNotHit" in array[count].keys():
    #             array[count]["LineNotHit"].append(linehitsplit[0])
    #         else:
    #             array[count]["LineNotHit"] = [linehitsplit[0]]
        
    if splitline[0] == "BRDA":
        if "Branch" in array[count].keys():
            brda = splitline[1].split(",")
            if brda[3] == "-" or 0:
                array[count]["Branch"].append([brda[0], brda[1]])
        else:
            array[count]["Branch"] = []
            brda = splitline[1].split(",")
            if brda[3] == "-" or 0:
                array[count]["Branch"].append([brda[0], brda[1]])
            
        
    if splitline[0] == "end_of_record":
        array.append({})
        count += 1

for i in range(0, count):
    logging.debug(array[i])
    filename = array[i]['SF']
    branches = array[i]['Branch']
    dict.update({filename: branches})
    
logging.debug(dict)

# TN: test name
# SF: source file path
# FN: line number,function name
# FNF:  number functions found
# FNH: number hit
# BRDA: branch data: line, block, (expressions,count)+
# BRF: branches found
# DA: line number, hit count
# LF: lines found
# LH:  lines hit.

#./genhtml.perl ./lcov.info -o coverage/html