import matplotlib.pyplot as plt
import json
import os

base_folderpath = os.path.expanduser("~/Downloads")
prepend_string = "ian_"
testcase_data = {
    "A": ["A1_ian", "A2_ian", "A3_ian", "A4_ian", "A5_ian"],
    "B": ["B6_ian", "B7_ian", "B8_ian", "B9_ian", "B10_ian"],
    "C": ["C11_ian", "C12_ian", "C13_ian", "C14_ian", "C15_ian"]
}

data = []
interesting_data_full = {}
time_data_full = {}

for testcase in testcase_data:
    stats_folders = testcase_data[testcase]
    # Open stats.json for each experiment
    print(f"\n\n===== Testcase {testcase} =====")
    for stats_folder in stats_folders:
        filepath = f"{base_folderpath}/{stats_folder}/stats.json"
        print(f"Reading from filepath: {filepath}")
        with open(filepath) as file:
            stat = file.readline()
            stat_json = json.loads(stat)
            data.append(stat_json)

    # Print out failures found
    def extract_failures(testcase_data):
        return map(lambda x: x["failed"], testcase_data)
    failures = []
    for i in data:
        failures += list(extract_failures(i))
    print(f"\nTotal failures: {sum(failures)}")

    # RQ1: #interesting test cases vs #tests
    print("\n---------------\nRQ1\n---------------")
    def extract_interesting_cumulative(testcase_data):
        non_failure_tests = filter(lambda x: not x["failed"], testcase_data)
        interesting_metric = map(lambda x: x["is_interesting"], non_failure_tests)
        interesting_count = 0
        cumulative_interesting = []
        for i in interesting_metric:
            interesting_count += i
            cumulative_interesting.append(interesting_count)
        return cumulative_interesting

    interesting_data = [extract_interesting_cumulative(x) for x in data]
    min_length = min([len(i) for i in interesting_data])
    interesting_average = []
    for i in range(min_length):
        current_testcases = [x[i] for x in interesting_data]
        interesting_average.append(sum(current_testcases) / len(current_testcases))
    interesting_data_full[testcase] = interesting_average

    plt.clf()
    plt.plot(interesting_average)
    plt.title("RQ1: Interesting test cases found against\n number of test cases (averaged over 5 experiments)")
    graph_filepath = f"{prepend_string}testcase_{testcase}_interesting_average.png"
    plt.savefig(graph_filepath)
    print(f"RQ1 saved as {graph_filepath}")

    # RQ2: Average time taken
    print("\n---------------\nRQ2\n---------------")
    def extract_test_generation_time_ms(testcase_data):
        return map(lambda x: x["test_generation_ns"] / 1000000, testcase_data)

    def extract_test_run_time_ms(testcase_data):
        return map(lambda x: x["test_run_ns"] / 1000000, testcase_data)

    test_generation_ms = [extract_test_generation_time_ms(x) for x in data]
    test_generation_ms_flatmap = []
    for i in test_generation_ms:
        test_generation_ms_flatmap += i
    average_test_generation_ms = sum(test_generation_ms_flatmap) / len(test_generation_ms_flatmap)
    print(f"Average test generation (ms) over {len(test_generation_ms_flatmap)} tests: {average_test_generation_ms} ms")

    test_run_ms = [extract_test_run_time_ms(x) for x in data]
    test_run_ms_flatmap = []
    for i in test_run_ms:
        test_run_ms_flatmap += i
    average_test_run_ms = sum(test_run_ms_flatmap) / len(test_run_ms_flatmap)
    print(f"Average test run (ms) over {len(test_run_ms_flatmap)} tests: {average_test_run_ms} ms")

    time_data_full[testcase] = (average_test_generation_ms, average_test_run_ms)

# Save timing data to csv
timing_filepath = f"{prepend_string}testcase_{"_".join(testcase_data.keys())}_timing.csv"
with open(timing_filepath, "w") as file:
    file.write("testcase,generation_ms,run_ms\n")
    for testcase, timings in time_data_full.items():
        file.write(f"{testcase},{timings[0]},{timings[1]}\n")
print(f"Timing data saved to {timing_filepath}")

# RQ3: Ablation study
print("\n---------------\nRQ3\n---------------")
plt.clf()
for testcase in testcase_data:
    plt.plot(interesting_data_full[testcase], label=f"Testcase {testcase}")
plt.title("RQ3: Ablation study of chunk+content mutation,\nchunk mutation only and content mutation only")
plt.legend()
graph_filepath = f"{prepend_string}testcase_{"_".join(testcase_data.keys())}_ablation.png"
plt.savefig(graph_filepath)
print(f"RQ3 saved as {graph_filepath}")