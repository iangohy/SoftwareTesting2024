from smart_fuzzer.schunk import SChunk
from smart_fuzzer.chunkTreeGenerator import ChunkTreeGenerator

def main():
    seed_file = "smart_fuzzer/sample_seed_inputs/django_seed.ini"

    tree_generator = ChunkTreeGenerator(seed_file)
    django_chunk_tree_root = tree_generator.generate_chunk_tree()
    
    print(django_chunk_tree_root.get_children())

    django_chunk_tree_root.mutate_chunks()

    print(django_chunk_tree_root.get_children())
    print(django_chunk_tree_root.get_children()[0])
    print(django_chunk_tree_root.get_children()[0].chunk_name)

    django_chunk_tree_root.mutate_contents()

    print(django_chunk_tree_root.get_children()[0].chunk_content)
    print(django_chunk_tree_root.get_children()[1].chunk_content)
    print(django_chunk_tree_root.get_children()[2].chunk_content)

    # for i in range(10):
    #     output_chunk = django_chunk.mutate()
    #     django_chunk.write_output("smart_fuzzer/mutation_outputs/django_outputs.txt", output_chunk)

if __name__ == "__main__":
    main()