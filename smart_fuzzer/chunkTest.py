from smart_fuzzer.schunk import SChunk
from smart_fuzzer.chunkTreeGenerator import ChunkTreeGenerator
import logging

streamhandler = logging.StreamHandler()
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", 
    level=logging.DEBUG,
    handlers=[
        streamhandler
    ]
)


def main():
    seed_file = "./django_seed_1_sample.ini"

    tree_generator = ChunkTreeGenerator(seed_file)
    django_chunk_tree_root = tree_generator.generate_chunk_tree()

    ### Verify tree structure    
    root_children = django_chunk_tree_root.get_children()
    print("root_children:", root_children)
    assert(len(root_children) == 2)

    endpoint_children = root_children["endpoint"].get_children()
    print("endpoint_children:", endpoint_children)
    assert(len(endpoint_children) == 3)

    for leaf_endpoint in endpoint_children.values():
        # Leaf nodes should have no children
        assert(len(leaf_endpoint.get_children()) == 0)

    ### Test get content
    endpoint_content = django_chunk_tree_root.get_lookup_chunk("endpoint").get_content()
    print("endpoint_content:", endpoint_content)
    assert(endpoint_content == "datatb/product/add/")

    payload_content = django_chunk_tree_root.get_lookup_chunk("payload").get_content()
    print("payload_content:", payload_content)
    assert(payload_content == {"name": "abc", "info": "abcd", "price": "1.2"})

    ### Test mutation
    django_chunk_tree_root.mutate_chunk_tree()

    print(django_chunk_tree_root.get_children())
    #print(django_chunk_tree_root.get_children()['endpoints'].get_children())

    print("\n===== After Chunk Mutation =====")
    endpoint_content = django_chunk_tree_root.get_lookup_chunk("endpoint").get_content()
    print("endpoint_content:", endpoint_content)
    payload_content = django_chunk_tree_root.get_lookup_chunk("payload").get_content()
    print("payload_content:", payload_content)

    django_chunk_tree_root.mutate_contents()
    
    # for i in range(10):
    #     output_chunk = django_chunk.mutate()
    #     django_chunk.write_output("smart_fuzzer/mutation_outputs/django_outputs.txt", output_chunk)

if __name__ == "__main__":
    main()