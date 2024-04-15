from enum import Enum
import logging
import json
import matplotlib.pyplot as plt

class EnergyAssignmentMode(Enum):
    DISTANCE = 1
    HASH = 2

class StatsCollector:
    data = []
    fuzzing_cycles_completed = 0

    def __init__(self, log_folderpath, mode=EnergyAssignmentMode.HASH):
        self.log_folderpath = log_folderpath
        self.mode = mode
        self.logger = logging.getLogger(__name__)
        
    def add_teststats(self, test_generation_ns, test_run_ns, failed, is_interesting_stats):
        test_stat = ({
            "test_generation_ns": test_generation_ns,
            "test_run_ns": test_run_ns,
            "failed": failed,
            "is_interesting_stats": is_interesting_stats["hash"] if self.mode == EnergyAssignmentMode.HASH else is_interesting_stats["distance"]
        })
        self.data.append(test_stat)
        self.logger.info(f"Collected stats: {test_stat}")

    def complete_fuzzing_cycle(self):
        self.fuzzing_cycles_completed += 1
        self.save_stats()
        self.log_current_stats()

    def get_fuzzing_cycles_completed(self):
        self.fuzzing_cycles_completed += 1

    def get_current_testnum(self):
        return len(self.data) + 1

    def log_current_stats(self):
        failures = sum(map(lambda x: x["failed"], self.data))
        unique_states = set(map(lambda x: x["is_interesting_stats"], self.data))
        stats = """
                    ______
                 .-'      `-.
               .'            `.
              /                \\
             ;                 ;\\
             |                 |;\\
             ;                 ;| \\
                                   \\
             '\               / ;   \\
              \`.           .' /     \\
               `.`-._____.-' .'       \\
                 / /`_____. '          \\
                / / / \                 \\
               / / /   '\                \\
              / / /      '\               \\
             / / /         '\              \\
            / / /            '\             \\
           / / /               '\            \\
          / / /                  '\           \     (             )
         / / /                     '\          \     (    (      )
        / / /                        '\         \     (      )  )
        \/_/                           '\        \     (      )
                                         '\       \    (  (  )
                                           '\      \    (     )
                                             '\     \    (    )
                                               '\    \    (   )
                                                 '\   \    ) )
                                                   '\  \   ()  Help!!
                                                     '\ \ ()   I'm Melting!
                                                       '\\(   |\__
                                                      ____$__/ ___>
                                                     /        /
                                                    /\   bug  )
                                                   |  \\-----((
                                                  __-- )) ----))--__
                                                --__            __ --
                                                   __------____--
"""
        stats += "\n\n===== Current Fuzzing Stats =====\n" + \
            f"Total fuzz cycles completed: {self.fuzzing_cycles_completed}\n" + \
            f"Total test cases ran: {len(self.data)}\n" + \
            f"Total failure cases found: {failures}\n" + \
            f"Unique state [{self.mode}] encountered: {len(unique_states)} [{unique_states}]\n"
        stats += "==============================\n\n\n\n"
        self.logger.info(stats)

    def save_stats(self):
        with open(f"{self.log_folderpath}/stats.json", "w") as file:
            file.write(json.dumps(self.data))

    def plot_crashes(self):
        failure = map(lambda x: x["failed"], self.data)
        failure_count = 0
        cumulative_failures = []
        for i in failure:
            failure_count += i
            cumulative_failures.append(failure_count)

        plt.clf()
        plt.plot(cumulative_failures)
        plt.title("Graph of crashes against number of test cases")
        plt.savefig(f"{self.log_folderpath}/crashes.png")


    def plot_is_interesting(self):
        interesting_metric = map(lambda x: x["is_interesting_stats"], self.data)
        metric_set = set()
        cumulative_metric = []
        for i in interesting_metric:
            metric_set.add(i)
            cumulative_metric.append(len(metric_set))

        plt.clf()
        plt.plot(cumulative_metric)
        plt.title("Graph of coverage paths against number of test cases")
        plt.savefig(f"{self.log_folderpath}/interesting.png")