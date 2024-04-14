from enum import Enum
import logging

class EnergyAssignmentMode(Enum):
    DISTANCE = 1
    HASH = 2

class StatsCollector:
    data = []
    fuzzing_cycles_completed = 0

    def __init__(self, mode=EnergyAssignmentMode.HASH):
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

    def get_fuzzing_cycles_completed(self):
        self.fuzzing_cycles_completed += 1

    # def current_stats(self):
    #     stats = "\n\n===== Fuzzing Stats =====\n" + \
    #         f"Total fuzz cycles completed: {self.fuzz_cycles_completed}\n" + \
    #         f"Total test cases ran: {self.total_test_cases_ran}\n" + \
    #         f"Total failure cases found: {self.total_failures_found}\n" + \
    #         f"Items remaining in SeedQ: {len(self.seedQ)}\n" + \
    #         f"Unique state [{self.energy_strat}] encountered: {len(self.unique_states)} [{self.unique_states}]\n"


        stats += "=============================="
        logger.info(stats)

    def plot_crashes(self):
        pass

    def plot_is_interesting(self):
        pass