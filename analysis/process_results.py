import matplotlib.pyplot as plt
import json
import os
import pandas as pd

base_folderpath = os.path.expanduser("~/Downloads")

prepend_string = "django_final_"
testcase_data = {
    "A": ["A1_v2", "A2_v2", "A3_v2", "A4_v2", "A5_v2"],
    "B": ["B6_v2", "B7_v2", "B8_v2", "B9_v2", "B10_v2"],
    "C": ["C11_v2", "C12_v2", "C13_v2", "C14_v2", "C15_v2"],
    # "X": ["X100_v2", "X101_v2", "X102_v2", "X103_v2", "X104_v2"]
}
# Manually input as have to verify whether crash is unique
unique_crashes_count = {
    "A": [69, 69, 69, 69, 69],
    "B": [69, 69, 69, 69, 69],
    "C": [69, 69, 69, 69, 69],
    "X": [69, 69, 69, 69, 69],
}

# prepend_string = "django_chrisw_"
# testcase_data = {
#     "A": ["A1_chrisw", "A2_chrisw", "A3_chrisw", "A4_chrisw", "A5_chrisw"],
#     "B": ["B6_chrisw", "B7_chrisw", "B8_chrisw", "B9_chrisw", "B10_chrisw"],
#     "C": ["C11_chrisw", "C12_chrisw", "C13_chrisw", "C14_chrisw", "C15_chrisw"]
# }

### Done
# prepend_string = "coap_chrisL_"
# testcase_data = {
#     "D": ["D16_chrisL", "D17_chrisL", "D18_chrisL", "D19_chrisL", "D20_chrisL"],
#     "E": ["E21_chrisL", "E22_chrisL", "E23_chrisL", "E24_chrisL", "E25_chrisL"],
#     "F": ["F26_chrisL", "F27_chrisL", "F28_chrisL", "F29_chrisL", "F30_chrisL"],
#     "Y": ["Y105_chrisL", "Y106_chrisL", "Y107_chrisL", "Y108_chrisL", "Y109_chrisL"]
# }

### Done
# prepend_string = "coap_YJ_"
# testcase_data = {
#     "D": ["D16_YJ", "D17_YJ", "D18_YJ", "D19_YJ", "D20_YJ"],
#     "E": ["E21_YJ", "E22_YJ", "E23_YJ", "E24_YJ", "E25_YJ"],
#     "F": ["F26_YJ", "F27_YJ", "F28_YJ", "F29_YJ", "F30_YJ"]
# }

### Done
# prepend_string = "ble_ian_"
# testcase_data = {
#     "G": ["G31_ian", "G32_ian", "G33_ian", "G34_ian", "G35_ian"],
#     "H": ["H36_ian", "H37_ian", "H38_ian", "H39_ian", "H40_ian"],
#     "I": ["I41_ian", "I42_ian", "I43_ian", "I44_ian", "I45_ian"],
#     "Z": ["Z110_ian", "Z111_ian", "Z112_ian", "Z113_ian", "Z114_ian"]
# }

### Done
# prepend_string = "ble_jiahui_"
# testcase_data = {
#     "G": ["G31_jiahui", "G32_jiahui", "G33_jiahui", "G34_jiahui", "G35_jiahui"],
#     "H": ["H36_jiahui", "H37_jiahui", "H38_jiahui", "H39_jiahui", "H40_jiahui"],
#     "I": ["I41_jiahui", "I42_jiahui", "I43_jiahui", "I44_jiahui", "I45_jiahui"],
#     "Z": ["Z110_jiahui", "Z111_jiahui", "Z112_jiahui", "Z113_jiahui", "Z114_jiahui"]
# }

interesting_data_full = {}
time_data_full = {}

for testcase in testcase_data:
    data = []
    stats_folders = testcase_data[testcase]
    # Open stats.json for each experiment
    print(f"\n\n===== Testcase {testcase} =====")
    for stats_folder in stats_folders:
        filepath = f"{base_folderpath}/{stats_folder}/stats.json"
        print(f"Reading from filepath: {filepath}")
        with open(filepath) as file:
            stat = file.readline()
            json_data = json.loads(stat)
            data.append(json_data)

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
    plt.title(f"RQ1: Testcase {testcase} - Interesting test cases found\n against number of test cases (averaged over 5 experiments)")
    graph_filepath = f"{prepend_string}testcase_{testcase}_r1_interesting_average.png"
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

    # RQ4: Stability
    print("\n---------------\nRQ4\n---------------")
    plt.clf()
    width = 0.4
    testcase_interesting_found = [x[-1] for x in interesting_data]
    unique_crashes = unique_crashes_count[testcase]

    df = pd.DataFrame({ 
        "Testcase": [i.split("_")[0] for i in stats_folders],
        "Unique Crashes": unique_crashes,
        "Interesting test cases": testcase_interesting_found 
    }) 
  
    ax = df.plot(x="Testcase", y=["Interesting test cases", "Unique Crashes"], kind="bar", title=f"RQ4: Stability study of Testcase {testcase}")
    graph_filepath = f"{prepend_string}testcase_{testcase}_stability.png"
    ax.get_figure().savefig(graph_filepath)
    print(f"RQ4 saved as {graph_filepath}")

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
