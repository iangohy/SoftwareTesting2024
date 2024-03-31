import logging
from greybox_fuzzer.mutator import Mutator
from typing import Any, List
import random
from oracle.oracle import Oracle
from smart_fuzzer.smartChunk import SmartChunk
import math


logger = logging.getLogger(__name__)

class MainFuzzer:
    def __init__(self, seedQ: List[Any], oracle: Oracle, max_fuzz_cycles=10, energy_strat='state_hash'):
        # state_hash or distance, first is hash, second is a number
        self.seedQ = seedQ
        self.failureQ = []
        self.oracle = oracle
        self.max_fuzz_cycles = max_fuzz_cycles
        self.mutator = Mutator(None, mode='ascii') # set the mode here, seed here is for random
        self.seed_idx = 0
        self.first_flag = True # flag to check if first run of fuzzer
        self.prev_energy = 100
        self.energy = 100
        # store parent seed validity
        self.validity= 0

        
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
        
    def assign_energy(self, seed):
        # if first run, default fuzz 100 times
        if self.first_flag:
            self.first_flag = False
            self.energy = 100
        else:
        # return energy based on the previous oracle status
        # possible ways is unique path, coverage, validity (syntactically)
            previous_validity = self.validity
            # divide by log to reduce the fuzzing of higher density regions? dk if it works or not
            self.energy = 100 + (self.prev_energy * (previous_validity / math.log(self.energy)))
        return self.energy
    
    def choose_next(self) -> SmartChunk:
        # Randomly choose an item from the seed q and pop out
        seed = self.seedQ.pop(random.randint(0, len(self.seedQ)-1))
        return seed
    
    def mutate(self):
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
                next_input = self.choose_next()
            except Exception as e:
                logger.error("Unable to obtain next_input")
                logger.exception(e)
                return
            
            energy = self.assign_energy()
            valid_inputs = 0
            for i in range(energy):
                logger.info(f">> Energy cycle: {i+1}/{energy}")
                mutated_chunk = next_input.mutate()
                failure, isInteresting, info = self.send_to_oracle(mutated_chunk)
                logger.info(f"Test result: failure {failure} | isInteresting {isInteresting} | info {info}")
                # get validity info from oracle
                valid_inputs += 1
                if failure:
                    # Add to failure queue
                    self.failureQ.append(mutated_chunk)
                elif isInteresting:
                    self.seedQ.append(mutated_chunk)
            # record the validity of this previous seed
            self.validity = self.degree_of_validity(next_input, valid_inputs)
            self.prev_energy = energy
        return self.seedQ, self.failureQ 

    def send_to_oracle(self, chunk):
        return self.oracle.run_test(chunk)

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
        self.chunk = SmartChunk()
        
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