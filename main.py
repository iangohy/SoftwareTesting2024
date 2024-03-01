from oracle.oracle import Oracle
import time
import logging

logger = logging.getLogger(__name__)
streamhandler = logging.StreamHandler()
filehandler = logging.FileHandler("tester.log")
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", 
    level=logging.DEBUG,
    handlers=[
        filehandler,
        streamhandler
    ]
)

# TODO: User will start program here

if __name__ == "__main__":
    logger.error("Coming soon...")