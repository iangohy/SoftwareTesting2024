from schunk import SChunk
from chunkTreeGenerator import ChunkTreeGenerator

def main():
    seed_file = "./django_seed_1_sample.ini"

    tree_generator = ChunkTreeGenerator(seed_file)
    django_chunk_tree_root = tree_generator.generate_chunk_tree()
    
    print(django_chunk_tree_root.get_children())

    django_chunk_tree_root.mutate_chunk_tree()

    print(django_chunk_tree_root.get_children())
    #print(django_chunk_tree_root.get_children()['endpoints'].get_children())

    django_chunk_tree_root.mutate_contents()

    print(django_chunk_tree_root.get_children()['endpoints'].get_children()['endpoint0'])

    # for i in range(10):
    #     output_chunk = django_chunk.mutate()
    #     django_chunk.write_output("smart_fuzzer/mutation_outputs/django_outputs.txt", output_chunk)

if __name__ == "__main__":
    main()