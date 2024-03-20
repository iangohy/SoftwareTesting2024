import random
import string

class Mutator:
    """A mutator 
    Args:
            mode (str): either "ascii" or "unicode" or "byte" or "int", default ascii
    Returns:
            bytesarray: for "byte" mode only
            str: the mutated string (for all other modes)
    """
    def __init__(self, seed, mode="ascii"):
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
    
