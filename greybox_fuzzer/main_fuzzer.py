import logging
from greybox_fuzzer.mutator import Mutator
from typing import Any, List
import random
from oracle.oracle import Oracle
import copy

from smart_fuzzer.schunk import SChunk


logger = logging.getLogger(__name__)

class MainFuzzer:
    def __init__(self, seedQ: List[Any], oracle: Oracle, max_fuzz_cycles=10, energy_strat='State Hash', exponent=2):
        """
        seedQ[i]"State Hash" or "Distance", first is hash, second is a number
        energy_strat = 'State Hash' OR 'Distance'
        """
        self.seedQ = seedQ
        self.failureQ = []
        self.oracle = oracle
        self.max_fuzz_cycles = max_fuzz_cycles
        # TODO remove unused
        self.mutator = Mutator(None, mode='ascii') # set the mode here, seed here is for random
        self.seed_idx = 0
        self.first_flag = True # flag to check if first run of fuzzer
        self.prev_energy = 100
        self.energy = 100
        self.energy_strat = energy_strat
        self.path_ids = {"ORIGINAL_PATH":1}
        self.total_distance = 1
        self.num_dist = 1
        self.total_paths_reached = 1
        self.exponent = exponent
        # store parent seed validity
        self.validity= 0
        # store some stats to report
        self.fuzz_cycles_completed = 0
        self.total_test_cases_ran = 0
        self.total_failures_found = 0
        self.unique_states = set()


        
    def reset(self):
        self.energy = 100
        self.first_flag = True
            
    def set_seed(self, seed):
        """reset seeds of fuzzer to new seed"""
        self.original_seed = seed
        self.seed = seed
        
    def degree_of_validity(self, seed, valid_inputs):
        self.validity = valid_inputs / self.energy
        return valid_inputs / self.energy
        
    def assign_energy(self, seed: tuple):
        """seed is a tuple (chunk, state) chunk: SmartChunk, state: distance(int), pathid hash(string) or None"""
        # if first run, default fuzz 100 times
        if self.first_flag or seed[1]==None:
            self.first_flag = False
            # TODO: increase in the future but we start small for now
            self.energy = 3
        elif self.energy_strat == "hash":
            # calculate based on path id
            hash = seed[1]["hash"] 
            self.path_ids[hash] += 1
            times_cur_path_reached = self.path_ids[hash]
            self.total_paths_reached += 1
            mean_freq = self.total_paths_reached / len(self.path_ids) 
            if times_cur_path_reached > mean_freq:
                # dont fuzz this if the frequency is zero
                self.energy = 0 
                # TODO maybe move to position 0? else every single seed mutated from a popular 
                # path will be skipped entirely
            else:
                # maximum of 150 000 for high freq paths
                self.energy = min((150 / 1.5 * (2 ** times_cur_path_reached), 150000))
            # TODO: does this cause duplicate addition since we already add hash above
            self.path_ids[hash] += 1 # increment because hash has been hit
        elif self.energy_strat == "dist":
            # calculate based on coverage of missing branches, larger => more missing branches hit
            # ie has travelled further
            # assign high energy if the average dist has increased
            dist = seed[1]["dist"] 
            self.total_distance += dist
            self.num_dist += 1
            avg_dist = self.total_distance / self.num_dist
            # TODO investigate this effectiveness 
            self.energy = min(150 / 1.5 * (2 ** avg_dist),150000)
        else:
            logger.error("assign_energy: energy_strat value is wrong")
            # validity code -> doesnt work if chunk is always syntactically correct
            # need to for loop the seedQ and retroactively assign validity based on some value
            # previous_validity = self.validity
            # # divide by log to reduce the fuzzing of higher density regions? dk if it works or not
            # self.energy = 100 + (self.prev_energy * (previous_validity / math.log(self.energy)))
        return self.energy
    
    def choose_next(self) -> SChunk:
        """Randomly choose an item from the seed q and pop out, seed is a tuple of 2"""
        seed = self.seedQ.pop(random.randint(0, len(self.seedQ)-1))
        return seed
    
    def mutate(self):
        # unused, TODO remove when confirmed unused
        mutated_seed = self.mutator.mutate(mutated_seed)
        self.seedQ.append(mutated_seed)
        
    def getQueues(self):
        """Return seedQ and failureQ"""
        return self.seedQ, self.failureQ

        
    def fuzz(self):
        """Follow greybox fuzzing algorithm, return seedQ and failureQ"""
        for fuzz_cycle_num in range(self.max_fuzz_cycles):
            logger.info(f">>>> Starting fuzzing cycle {fuzz_cycle_num + 1}")

            try:
                next_seed = self.choose_next()
            except Exception as e:
                logger.error("Unable to obtain next_input, assuming completed")
                logger.exception(e)
                self.log_stats()
                return
            
            energy = self.assign_energy(next_seed)
            next_input, _ = next_seed
            valid_inputs = 0
            for i in range(energy):
                logger.debug(f"next_input: {next_input}")
                mutated_chunk = copy.deepcopy(next_input)
                logger.info(f">> Energy cycle: {i+1}/{energy}")
                mutated_chunk.mutate_chunks()
                # TODO: enable content mutation once invalid syntax handling
                # is implemented
                # mutated_chunk.mutate_contents()

                failure, isInteresting, info = self.send_to_oracle(mutated_chunk)
                logger.info(f"Test result: failure {failure} | isInteresting {isInteresting} | info {info}")
                if self.energy_strat == "State Hash":
                    self.unique_states.add(info.get("hash"))
                elif self.energy_strat == "Distance":
                    self.unique_states.add(info.get("dist"))
                # get validity info from oracle
                valid_inputs += 1
                if failure:
                    # Add to failure queue
                    self.failureQ.append(mutated_chunk)
                    self.total_failures_found += 1
                elif isInteresting:
                    data = None
                    if self.energy_strat == "Distance":
                        data = info.get("dist")
                    elif self.energy_strat == "State Hash":
                        data = info.get("hash")
                    else:
                        data = None
                    self.seedQ.append((mutated_chunk, data))
                self.total_test_cases_ran += 1
            # record the validity of this previous seed
            self.validity = self.degree_of_validity(next_input, valid_inputs)
            self.prev_energy = energy
            self.fuzz_cycles_completed += 1
            self.log_stats()
        return 

    def send_to_oracle(self, chunk):
        """
        Returns:
            failure: bool, isInteresting:bool, info: {"hash": string} OR info: {"dist": non-neg number}
        """
        return self.oracle.run_test(chunk)

    def log_stats(self):
        stats = "\n\n===== Fuzzing Stats =====\n" + \
            f"Total fuzz cycles completed: {self.fuzz_cycles_completed}\n" + \
            f"Total test cases ran: {self.total_test_cases_ran}\n" + \
            f"Total failure cases found: {self.total_failures_found}\n" + \
            f"Items remaining in SeedQ: {len(self.seedQ)}\n" + \
            f"Unique state [{self.energy_strat}] encountered: {len(self.unique_states)} [{self.unique_states}]\n"


        stats += "=============================="
        logger.info(stats)

if __name__ == '__main__':
    seedQ = []
    failureQ = []
    seed = "This is a test seed."
    mainfuzzer = MainFuzzer(seed, seedQ, failureQ)
    mainfuzzer.fuzz()

class Seed:
    def __init__(self, data: str) -> None:
        """Initialize from seed data"""
        self.data = data
        self.chunk = SChunk()
        
        # TODO: adjust this based on fuzzer chunking etc
        self.energy = 0.0

    def __str__(self) -> str:
        """Returns data as string"""
        return self.data

    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, key): 
        return self.data[key]
        
    def __setitem__(self, key, value):
        self.data[key] = value
    
    __repr__ = __str__