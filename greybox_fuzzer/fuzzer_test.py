from mutation_fuzzer import MutationFuzzer, Seed

fuzzer = MutationFuzzer(None)

test_input1 = "The quick brown fox."    # utf-8 ASCII, so one byte per char
test_input2 = "Σὲ γνωρίζω ἀπὸ τὴν κόψη" # utf-8 greek, more than 1 byte -> 2 bytes

print(fuzzer.flip_bit(test_input1))
print(fuzzer.flip_bit(test_input2))
print("-----")

out1 = print(fuzzer.flip_byte(test_input1, 2))
out2 = print(fuzzer.flip_byte(test_input2, 2))
print("-----")
print(fuzzer.delete_random_char(test_input1, 2))
print("-----")
print(fuzzer.insert_random_ascii(test_input1, 2))
print("-----")
print(fuzzer.insert_random_utf(test_input1, 2))
print("-----")

try:
    print(out1.decode('latin1'))
except:
    print("Cannot decode out1")
try:
    print(out2.decode())
except:
    print("Cannot decode out2")