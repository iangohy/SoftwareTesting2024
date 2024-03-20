from coverage import Coverage
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

def test_function(x):
    i = 0
    y = 0
    while i < 100:
        if x[i] < 5:
            y += 1
        else:
            y -= 1
        i += 1
    assert(y <= 100)

input_list = [
    # interesting; if*100
    [0] * 100,
    # interesting; different branch; else*100
    [10] * 100,
    # not interesting; since 50 and 100 belong in the same bucket; if*50, else*50
    [0 if i < 50 else 10 for i in range(100)],
    # not interesting; if*50, else*50
    [10 if i < 50 else 0 for i in range(100)],
    # interesting; if*25, else*75
    [0 if i < 25 else 10 for i in range(100)],
    # interesting; if*75, else*25
    [10 if i < 25 else 0 for i in range(100)],
    # interesting; if*6, else*94
    [-1 if i < 5 else 100 for i in range(100)],
]

def main():
    for index, i in enumerate(input_list):
        logging.debug("\nInput {}".format(index))
        cov = Coverage()
        cov.start()
        test_function(i)
        cov.stop()

        executed_lines = cov.json_report(outfile="report{}".format(index))
        logging.debug(executed_lines)

if __name__ == "__main__":
    main()