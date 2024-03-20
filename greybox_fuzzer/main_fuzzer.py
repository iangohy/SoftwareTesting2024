import logging
from mutator import Mutator
from typing import Any, List
import random
# from oracle.oracle import Oracle

log = logging.getLogger(__name__)
log.info("Hello, world")

class MainFuzzer:
    def __init__(self, init_seed, seedQ: List[Any], failureQ:List[Any], mode='ascii'):
        self.original_seed = init_seed
        self.seed = init_seed
        self.seedQ = seedQ
        self.ori_seedQ_len = 1
        self.failureQ = failureQ
        # self.oracle = Oracle("sudifuzz_config_example.ini")
        self.mutator = Mutator(None, mode=mode) # set the mode here, seed here is for random
        self.seed_idx = 0
            
    def set_seed(self, seed):
        """reset seeds of fuzzer to new seed"""
        self.original_seed = seed
        self.seed = seed
        
    def assign_energy(self):
        for seed in self.seedQ:
            seed.energy = 1
    
    def choose_next(self):
        seed = random.choices(self.seedQ)
        return seed
    
    def generate_mutations_ten(self):
        """generate 10 consecutive mutations and append to self.seedQ"""
        mutated_seed = self.seed
        for _ in range(0,10):
            mutated_seed = self.mutator.mutate(mutated_seed)
            self.seedQ.append(mutated_seed)
        return
        
    def getQueues(self):
        """Return seedQ and failureQ"""
        return self.seedQ, self.failureQ
        
    def fuzz(self):
        """Send all seeds at least once to oracle, else fuzz one seed and send to oracle, return seedQ and failureQ"""
        input_seed = None
        if self.seed_idx < self.ori_seedQ_len:
            # currently seedQ should only start with one seed
            input_seed = self.seedQ[self.seed_idx]
            self.seed_idx += 1
        else:
            # mutate an input and append to seedQ
            new_seed = self.choose_next()
            new_seed = self.mutator.mutate_n_times(new_seed, n=3)
            self.seedQ.append(new_seed)
            input_seed = new_seed
        # TODO send to oracle, if failure received, append to failureQ
        result = self.send_to_oracle(input_seed)
        if result == False:
            self.failureQ.append(input_seed)
        return self.seedQ, self.failureQ
        
    # def fuzz_hundred(self):
    #     for _ in range(0,100):
    #         input = self.seedQ.pop() # pop last
    #         # TODO send to oracle
        
    def send_to_oracle(self, seed):
        # TODO write send to oracle, return False if crashed else return True
        return True

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