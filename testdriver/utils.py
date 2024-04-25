import logging, os, re

from testdriver.custom_exceptions import TestDriverCrashDetected

logger = logging.getLogger(__name__)

def check_for_blacklist_phrase(line: str, blacklist: list):
    logger.debug(f"Checking for blacklisted words in: {line}")
    for blacklist_phrase in blacklist:
            if blacklist_phrase.lower() in line.lower():
                raise TestDriverCrashDetected(f"blacklist phrase [{blacklist_phrase}] detected")
            
def sanitize_input(input_str:str):
    # Escape special characters and backslashes
    input_str = repr(input_str)[1:-1]

    sanitized_string = ""
    
    # Handle quotation marks
    for char in input_str:
        if char == "'" or char == '"':
            # Check if the quote is already preceded by a backslash
            if sanitized_string and sanitized_string[-1] == '\\':
                sanitized_string += char
            else:
                sanitized_string += '\\' + char
        else:
            sanitized_string += char

    sanitized_string = re.sub(r'[^\x00-\x7F]+', '', sanitized_string)

    return sanitized_string

def clean_gen_files():
    files = [
        '/testdriver/missing_branches.json',
        '/testdriver/missing_lines.json',
        '/testdriver/output.json',
        '/testdriver/test_case.py',
        '/.coverage',
        '/coap_fuzz.log'
    ]

    logging.info("Cleaning directory of old generated files.")

    for file in files:
        if os.path.exists(os.getcwd()+file):
            os.remove(os.getcwd()+file)