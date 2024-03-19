from smartChunk import SmartChunk
from input_models.djangoDict import DjangoDict

def main():
    seed_file = open("smart_fuzzer/seed_inputs/django_seed.txt", "r")
    seed_string = seed_file.readline()
    seed_file.close()

    django_chunk = SmartChunk(DjangoDict(),
                              seed_string)
    
    django_chunk.get_chunks(django_chunk.chunk_content)

    for i in range(10):
        django_chunk.mutate()

if __name__ == "__main__":
    main()