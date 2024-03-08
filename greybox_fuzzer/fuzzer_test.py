from mutation_fuzzer import MutationFuzzer

fuzzer = MutationFuzzer(None)

test_input1 = "The quick brown fox."    # utf-8 ASCII, so one byte per char
test_input2 = "Σὲ γνωρίζω ἀπὸ τὴν κόψη" # utf-8 greek, more than 1 byte -> 2 bytes

print(fuzzer.fuzz_string(test_input1))
print(fuzzer.fuzz_string(test_input2))

out1 = fuzzer.fuzz_bytes(test_input1, 2,3)
out2 = fuzzer.fuzz_bytes(test_input2, 2,3, encoding="utf-8")
print(out1)
print(out2)
try:
    print(out1.decode('latin1'))
except:
    print("Cannot decode out1")
try:
    print(out2.decode())
except:
    print("Cannot decode out2")