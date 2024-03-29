import logging

from testdriver.custom_exceptions import TestDriverCrashDetected

logger = logging.getLogger(__name__)

def check_for_blacklist_phrase(line: str, blacklist: list):
    logger.debug(f"Checking for blacklisted words in: {line}")
    for blacklist_phrase in blacklist:
            if blacklist_phrase.lower() in line.lower():
                raise TestDriverCrashDetected(f"blacklist phrase [{blacklist_phrase}] detected")