import json, random, logging
from IsInteresting import is_interesting

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
    # interesting; if*5, else*95
    [-1 if i < 5 else 100 for i in range(100)],
]

random_input_list = [
    [random.randint(0, 100) for _ in range(100)],
    [random.randint(0, 100) for _ in range(100)],
    [random.randint(0, 100) for _ in range(100)],
    [random.randint(0, 100) for _ in range(100)],
    [random.randint(0, 100) for _ in range(100)],
]

def main():
    global_map = {}
    buckets = [1, 2, 3, 4, 8, 16, 32, 128] # tunable

    for index, i in enumerate(input_list):
        logging.debug("\nInput {}".format(index))
        is_interesting_result = is_interesting(test_function, i, global_map, buckets)
        # logging.debug(json.dumps(global_map, indent=4, sort_keys=True))
        logging.debug(is_interesting_result)

if __name__ == "__main__":
    main()