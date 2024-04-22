import random
import string
from smart_fuzzer.chunk_logger import Logger
from enum import Enum

class ASCIIMutations(Enum):
    DELETE = 1
    FLIP_BIT = 2
    INSERT_RANDOM_ASCII = 3
    BIG_INSERT = 4
    NO_MUTATION = 5

class Mutator:
    """A mutator 
    Args:
            mode (str): either "ascii" or "unicode" or "byte" or "int", default ascii
    Returns:
            bytesarray: for "byte" mode only
            str: the mutated string (for all other modes)
    """
    def __init__(self, seed, mode="ascii"):
        self.logger = Logger("Content Mutation")
        self.mode = mode
        self.seed = seed
        self.mutators = [self.delete_random_char]
        modes = ['ascii', 'unicode', 'byte', "int"]
        # TODO add possibility to modify the chance of delete vs add vs replace/flip
        # maybe change to class based instead
        if mode not in modes:
            raise ValueError("Invalid mode. Expected one of: %s" % modes)
        if mode == "unicode":
            self.mutators.append(self.replace_random_utf)
            self.mutators.append(self.insert_random_utf)
        if mode == "byte":
            self.mutators = []
            self.mutators.append(self.flip_byte)
        if mode == "int":
            self.mutators = []
            self.mutators.append(self.replace_random_int)
            self.mutators.append(self.insert_random_int)
            self.mutators.append(self.delete_random_int)
        else:
            self.mutators.append(self.flip_bit)
            self.mutators.append(self.insert_random_ascii)
        self.setup()
    
    def mutate(self, string, start=0):  # to do: mod this to be Seed obj if needed
        """Main function to call when mutating a string"""
        mutator = random.choice(self.mutators)
        return mutator(string, start)
    
    def mutate_with_choice(self, string, ascii_mutation, start=0):  # to do: mod this to be Seed obj if needed
        """Function to call when mutating a string with a chosen ascii mutation"""
        mutator = None
        match ascii_mutation:
            case ASCIIMutations.DELETE:
                mutator = self.delete_random_char

            case ASCIIMutations.FLIP_BIT:
                mutator = self.flip_bit

            case ASCIIMutations.INSERT_RANDOM_ASCII:
                mutator = self.insert_random_ascii

            case ASCIIMutations.NO_MUTATION:
                mutator = self.no_mutation
                
            case ASCIIMutations.BIG_INSERT:
                mutator = self.multiply_input_100
            case _:
                raise Exception("No match for ASCII mutation")
            
        self.logger.log(f"content mutation for {string}: {ascii_mutation}")
                
        return mutator(string, start)
    
    def mutate_n_times(self, string, n=1, start=0):  # to do: mod this to be Seed obj if needed
        """Call when mutating more than once when mutating a string"""
        output = string
        for _ in range(0, n):
            if (len(output)==1):
                break
            mutator = random.choice(self.mutators)
            output = mutator(output, start)
        return output
    
    def mutate_n_times_with_choice(self, string, ascii_mutation, n=1, start=0):
        """Call when mutating more than once when mutating a string with a chosen ascii mutation"""
        output = string
        for _ in range(0, n):
            if (len(output)==1):
                break
            output = self.mutate_with_choice(output, ascii_mutation, start)
        return output

    def setup(self):
        if self.seed != None:
            random.seed(self.seed)
            
    def flip_bit(self, value, start=0):
        """Flips a single bit of a string in the first byte of a string in unicode (utf-8)

        Args:
            value (_type_): a string, in utf-8

        Returns:
            _type_: a new string
        """
        pos = random.randint(start, len(value) - 1)
        c = value[pos]
        bit_mask = 1 << random.randint(0, 7)
        new_c = chr(ord(c) ^ bit_mask)
        return value[:pos] + new_c + value[pos + 1:] # fastest way to replace a char
    
    def flip_byte(self, value, start=0):
        """Randomly create new byte in the middle of an input, utf-8 conforming not guarranteed

        Args:
            payload (_type_): payload 
            num_bytes (_type_): the number of bytes to randomize
            start_byte (_type_): the starting position, set to 3 for COAP to ignore header

        Returns:
            _type_: payload -> bytesarray
        """
        # start_byte = 3 if COAP because header is 4 bytes
        if isinstance(value, str):  
            value = bytes(value.encode("utf-8")) # payload is a utf-8 string
        fuzzed_bytes = bytes([random.getrandbits(8)])
        return b''.join([value[:start] , fuzzed_bytes , value[start:]])

    
    
    def replace_random_utf(self, value, start=0):
        pos = random.randint(start, len(value) - 1)
        new_utf_char = chr(random.randint(0, 1114111))
        return value[:pos] + new_utf_char + value[pos+1:]
    
    def insert_random_utf(self, value, start=0):
        pos = random.randint(start, len(value) - 1)
        new_utf_char = chr(random.randint(0, 1114111))
        return value[:pos] + new_utf_char + value[pos:]
         
        
    def insert_random_ascii(self, value, start=0):
        pos = random.randint(start, len(value) - 1)
        new_ascii_char = chr(random.randint(0, 127))
        return value[:pos] + new_ascii_char + value[pos:]
        
    def delete_random_char(self, value, start=0):
        pos = random.randint(start, len(value) - 1)
        return value[:pos] + value[pos + 1:]
    
    def insert_random_int(self, value, start=0):
        value = str(value)
        pos = random.randint(start, len(value) - 1)
        new_digit = chr(random.randint(48, 57))
        return value[:pos] + new_digit + value[pos:]
        
    def replace_random_int(self, value, start=0):
        value = str(value)
        pos = random.randint(start, len(value) - 1)
        new_digit = chr(random.randint(48, 57))
        return value[:pos] + new_digit + value[pos + 1:]
        
    def delete_random_int(self, value, start=0):
        value = str(value)
        pos = random.randint(start, len(value) - 1)
        return value[:pos] + value[pos + 1:]
    
    def no_mutation(self, value, start=0):
        return value
    
    def multiply_input_100(self, value, start=0):
        value = value * 100
        return value
