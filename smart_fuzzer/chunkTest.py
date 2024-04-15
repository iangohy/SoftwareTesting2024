from smart_fuzzer.schunk import SChunk
from smart_fuzzer.chunkTreeGenerator import ChunkTreeGenerator
import logging
import copy

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

    ### Verify mutation weights
    assert(django_chunk_tree_root.chunk_mutation_weights == [0.33, 0.33, 0.34])
    assert(django_chunk_tree_root.get_lookup_chunk("endpoint").chunk_mutation_weights == [0.2, 0.2, 0.6])

    ### Verify content mutation weights
    assert(django_chunk_tree_root.content_mutation_probability == 0.2)
    assert(django_chunk_tree_root.get_lookup_chunk("endpoint").get_children()["endpoint0"].content_mutation_probability == 0.1)

    ### Test get content
    endpoint_content = django_chunk_tree_root.get_lookup_chunk("endpoint").get_content()
    print("endpoint_content:", endpoint_content)
    assert(endpoint_content == "datatb/product/add/")

    payload_content = django_chunk_tree_root.get_lookup_chunk("payload").get_content()
    print("payload_content:", payload_content)
    assert(payload_content == {"name": "abc", "info": "abcd", "price": "1.2"})

    ### Test copying
    root_copy = copy.deepcopy(django_chunk_tree_root)
    root_copy_1 = copy.deepcopy(django_chunk_tree_root)

    assert(root_copy != django_chunk_tree_root)
    assert(root_copy_1 != django_chunk_tree_root)
    assert(root_copy != root_copy_1)

    assert(root_copy.get_children()["endpoint"] != root_copy_1.get_children()["endpoint"])
    print("root_copy lookup chunks:", root_copy.lookup_chunks)

    ### Test mutation

    root_copy.mutate_chunk_tree()
    root_copy_1.mutate_chunk_tree()
    root_copy.mutate_contents()
    root_copy_1.mutate_contents()

    root_copy_endpoint = root_copy.get_lookup_chunk("endpoint")
    root_copy_1_endpoint = root_copy_1.get_lookup_chunk("endpoint")
    assert(id(root_copy_1_endpoint) != id(root_copy_endpoint))
    print("root_copy_endpoint children:")
    for child in root_copy_endpoint.get_children().values():
        print(child.get_content())
    print("root_copy_1_endpoint children:")
    for child in root_copy_1_endpoint.get_children().values():
        print(child.get_content())

    # print(django_chunk_tree_root.get_children())
    #print(django_chunk_tree_root.get_children()['endpoints'].get_children())

    print("\n===== After Chunk Mutation =====")
    print("root_copy mutated")
    endpoint_content = root_copy.get_lookup_chunk("endpoint").get_content()
    print("endpoint_content:", endpoint_content)
    payload_content = root_copy.get_lookup_chunk("payload").get_content()
    print("payload_content:", payload_content)

    print("root_copy_1 mutated")
    endpoint_content = root_copy_1.get_lookup_chunk("endpoint").get_content()
    print("endpoint_content:", endpoint_content)
    payload_content = root_copy_1.get_lookup_chunk("payload").get_content()
    print("payload_content:", payload_content)

    django_chunk_tree_root.mutate_contents()
    
    # for i in range(10):
    #     output_chunk = django_chunk.mutate()
    #     django_chunk.write_output("smart_fuzzer/mutation_outputs/django_outputs.txt", output_chunk)

if __name__ == "__main__":
    main()