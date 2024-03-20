from mutator import Mutator
from main_fuzzer import Seed

fuzzer = Mutator(None)

test_input1 = "The quick brown fox."    # utf-8 ASCII, so one byte per char
test_input2 = "Σὲ γνωρίζω ἀπὸ τὴν κόψη" # utf-8 greek, more than 1 byte -> 2 bytes

# print(fuzzer.flip_bit(test_input1))
# print(fuzzer.flip_bit(test_input2))
# print("-----")

# out1 = print(fuzzer.flip_byte(test_input1, 2))
# out2 = print(fuzzer.flip_byte(test_input2, 2))
# print("-----")
# print(fuzzer.delete_random_char(test_input1, 2))
# print("-----")
# print(fuzzer.insert_random_ascii(test_input1, 2))
# print("-----")
# print(fuzzer.insert_random_utf(test_input1, 2))
# print("-----")

# try:
#     print(out1.decode('latin1'))
# except:
#     print("Cannot decode out1")
# try:
#     print(out2.decode())
# except:
#     print("Cannot decode out2")
    
## TODO , test using Seed object.

modes = ['ascii', 'unicode', 'byte']
fuzzer2 = Mutator(None, mode='ascii')
input3 = test_input1
input3 = 11111
input3 = Seed("foxy life")
for _ in range(1,100):
    input3 = fuzzer2.mutate_n_times(input3)
    print(input3)

print(int("-01"))