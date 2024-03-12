import random
import string

class MutationFuzzer:
    """A mutation fuzzer
    """
    def __init__(self, seed, mode="bitflip"):
        self.mode = mode
        self.seed = seed
        self.setup()
    
    def setup(self):
        if self.seed != None:
            random.seed(self.seed)
            
    def fuzz_string(self, value):
        """Flips a single bit of a string in the first byte of a string in unicode (utf-8)

        Args:
            value (_type_): a string, in utf-8

        Returns:
            _type_: a new string
        """
        pos = random.randint(0, len(value) - 1)
        c = value[pos]
        bit_mask = 1 << random.randint(0, 7)
        new_c = chr(ord(c) ^ bit_mask)
        return value[:pos] + new_c + value[pos + 1:] # fastest way to replace a char
    
    def fuzz_bytes(self, payload, num_bytes, start_byte, encoding="utf-8"):
        """Randomly create new byte in the middle of an input, utf-8 conforming not guarranteed

        Args:
            payload (_type_): payload 
            num_bytes (_type_): the number of bytes to randomize
            start_byte (_type_): the starting position, set to 3 for COAP to ignore header

        Returns:
            _type_: payload -> bytesarray
        """
        # start_byte = 3 if COAP because header is 4 bytes
        out = bytes(payload.encode(encoding)) # payload is a utf-8 string
        fuzzed_bytes = bytes([random.getrandbits(8) for _ in range(num_bytes)])
        return b''.join([out[:start_byte] , fuzzed_bytes , out[start_byte + num_bytes:]])