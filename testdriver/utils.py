import logging

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

    return sanitized_string