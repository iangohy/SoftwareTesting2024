import random
import configparser
from enum import Enum
from smart_fuzzer.chunk_logger import Logger
from smart_fuzzer.mutator import Mutator, ASCIIMutations
import copy

class ChunkType(Enum):
    OBJECT = 1
    STRING = 2
    KEYVALUE = 3

class ChunkMutate(Enum):
    ADD_CHUNK = 1
    REMOVE_CHUNK = 2
    NO_MUTATION = 3

class SChunk:
    def __init__(self, chunk_name, chunk_content=None, removable=False, children={}, lookup_chunks={}, chunk_mutation_weights = [0.33, 0.33, 0.34], chunk_type=ChunkType.STRING, content_mutation_weights=[0.25, 0.25, 0.25, 0.25]):
        self.chunk_name = chunk_name                            # Name of the chunk, corresponds to section name in seed config file
        self.chunk_content = chunk_content                      # Content in the chunk
        self.removable = removable                              # removable flag
        self.children = children                                # Dictionary of children chunks, children chunks may be removable or non-removable
        self.lookup_chunks = lookup_chunks                      # Dictionary of children chunks that are only non-removable
        self.chunk_mutation_weights = chunk_mutation_weights    # List of weights for choosing chunk mutations, in the order of the ChunkMutate Enum
        self.config = configparser.ConfigParser()
        self.logger = Logger("SmartChunk")
        self.type = chunk_type
        self.content_mutation_weights = content_mutation_weights
        self.content_mutator = Mutator(None)
    
    def get_children(self):
        return self.children
    
    def get_child(self, child_key):
        return self.children[child_key]

    def add_child(self, child_chunk):
        self.children[child_chunk.chunk_name] = child_chunk

        # Add child to lookup chunks if it is not removable
        if (not child_chunk.removable):
            self.lookup_chunks[child_chunk.chunk_name] = child_chunk
    
    def get_lookup_chunk(self, lookup_chunk_name):
        return self.lookup_chunks[lookup_chunk_name]

    # full mutation consists of 2 passes of mutations, 1 pass for chunk mutations, 1 pass for content mutation

    # mutate_chunk_tree mutates all chunks starting from the current chunk this function is called on
    def mutate_chunk_tree(self):
        if not self.children:
            return
        else:
            mutation = random.choices(list(ChunkMutate), self.chunk_mutation_weights)[0]
            output = list(self.children.items())
            self.logger.log(f"mutation for {self.chunk_name}: {mutation}")
            match mutation:
                case ChunkMutate.ADD_CHUNK:
                    output = self.add_chunk(output)

                case ChunkMutate.REMOVE_CHUNK:
                    output = self.remove_chunk(output)

                case ChunkMutate.NO_MUTATION:
                    output = output

            self.children = {}
            for tup in output:
                self.children[tup[1].chunk_name] = tup[1]

            for chunk in self.children.values():
                chunk.mutate_chunk_tree()

    # mutate_chunk mutates the current chunk's children only, if it has any
    def mutate_single_chunk(self):
        if not self.children:
            return
        else:
            mutation = random.choices(list(ChunkMutate), self.chunk_mutation_weights)
            output = list(self.children.items())
            match mutation:
                case ChunkMutate.ADD_CHUNK:
                    output = self.add_chunk(output)

                case ChunkMutate.REMOVE_CHUNK:
                    output = self.remove_chunk(output)

                case ChunkMutate.NO_MUTATION:
                    output = output

            self.children = {}
            for tup in output:
                self.children[tup[1].chunk_name] = tup[1]

    # Mutate chunk_content a random number of times, applying a random ascii mutation each time for n times
    # (e.g run ASCIIMutations.FLIP_BIT 3 times followed by ASCIIMutations.DELETE 2 times) 
    def mutate_contents(self):
        if not self.children:
            content_mutator = Mutator(None)
            for _ in range(random.randint(1, 2)):
                mutation = random.choices(list(ASCIIMutations), self.content_mutation_weights)[0]
                self.chunk_content = content_mutator.mutate_n_times_with_choice(string=self.chunk_content, ascii_mutation=mutation, n=random.randint(1, 10))

        else:
            for chunk in self.children.values():
                if isinstance(chunk, SChunk):
                    chunk.mutate_contents()
    
    def add_chunk(self, output):
        if (len(output) == 0):
            # If no children, add new chunk
            if self.type == ChunkType.KEYVALUE:
                return [SChunk("key", "aaaaa", True), SChunk("value", "bbbbb")]
            elif self.type == ChunkType.OBJECT:
                child_key = SChunk("key", "aaaaa", True)
                child_value = SChunk("value", "bbbbb")
                return [SChunk("keyvalue", removable=True, children={"key": child_key, "value": child_value}, chunk_type=ChunkType.KEYVALUE)]
            else:
                return [SChunk("name", "aaaaa", True)]
        new_chunk = copy.deepcopy(random.choice(output))
        new_chunk[1].chunk_name = new_chunk[1].chunk_name + "~"
        position = random.randrange(0, len(self.children))
        output.insert(position, new_chunk)

        return output
    
    def remove_chunk(self, output):
        if (len(output) == 0):
            return output
        
        chosen_chunk = random.choice(output)
        if (chosen_chunk[1].removable):
            output.remove(chosen_chunk)
        else:
            self.logger.log(f"remove_chunk ignoring {chosen_chunk[1].chunk_name} as it is not removable")

        return output
    
    def get_content(self):
        match self.type:
            case ChunkType.OBJECT:
                # Assume object holds children of key-value pairs
                res = {}
                for child in self.children.values():
                    res.update(child.get_content())
                return res

            case ChunkType.STRING:
                # Return concatenation of children content
                res = ""
                if len(self.children) == 0:
                    return self.chunk_content
                
                for child in self.children.values():
                    # self.logger.log(child)
                    # self.logger.log(child.get_content())
                    res += str(child.get_content())

                return res
            
            case ChunkType.KEYVALUE:
                # Key value pair only considers first two children
                if len(self.children) < 2:
                    return {}
                else:
                    key_string = list(self.children.values())[0].get_content()
                    value_string = list(self.children.values())[1].get_content()
                    return {f"{key_string}": value_string}
                    
            case _:
                raise RuntimeError(f"Unable to determine type of chunk {self}")
            
    def set_chunk_mutation_weights(self, weights):
        self.chunk_mutation_weights = weights

    def __str__(self):
        return f"SChunk name={self.chunk_name},content={self.chunk_content},num_children={len(self.children)},chunk_mutation_weights={self.chunk_mutation_weights},content_mutation_weights={self.content_mutation_weights}"
    
    def __repr__(self):
        return f"<SChunk Object id={id(self)},name={self.chunk_name},content={self.chunk_content},num_children={len(self.children)},removable={self.removable},chunk_mutation_weights={self.chunk_mutation_weights},content_mutation_weights={self.content_mutation_weights}>"
