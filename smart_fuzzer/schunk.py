import random
import configparser
from enum import Enum
from chunk_logger import Logger
from mutator import Mutator

class ChunkType(Enum):
    OBJECT = 1
    STRING = 2

class ChunkMutate(Enum):
    ADD_CHUNK = 1
    REMOVE_CHUNK = 2
    NO_MUTATION = 3

class SChunk:
    def __init__(self, chunk_name, chunk_content=None, modifiable=False, children={}, lookup_chunks={}, chunk_mutation_weights = [0.33, 0.33, 0.34], chunk_type=ChunkType.STRING):
        self.chunk_name = chunk_name                            # Name of the chunk, corresponds to section name in seed config file
        self.chunk_content = chunk_content                      # Content in the chunk
        self.modifiable = modifiable                            # modifiable flag
        self.children = children                                # Dictionary of children chunks, children chunks may be modifiable or non-modifiable
        self.lookup_chunks = lookup_chunks                      # Dictionary of children chunks that are only non-modifiable
        self.chunk_mutation_weights = chunk_mutation_weights    # List of weights for choosing chunk mutations, in the order of the ChunkMutate Enum
        self.config = configparser.ConfigParser()
        self.logger = Logger("SmartChunk")
        self.type = chunk_type
    
    def get_children(self):
        return self.children
    
    def get_child(self, child_key):
        return self.children[child_key]

    def add_child(self, child_chunk):
        self.children[child_chunk.chunk_name] = child_chunk

        # Add child to lookup chunks if it is not modifiable
        if (not child_chunk.modifiable):
            self.lookup_chunks[child_chunk.chunk_name] = child_chunk
    
    def get_lookup_chunk(self, lookup_chunk_name):
        return self.lookup_chunks[lookup_chunk_name]

    # full mutation consists of 2 passes of mutations, 1 pass for chunk mutations, 1 pass for content mutation

    # mutate_chunk_tree mutates all chunks starting from the current chunk this function is called on
    def mutate_chunk_tree(self):
        if not self.children:
            return
        elif not self.modifiable:
            for chunk in self.children.values():
                chunk.mutate_chunk_tree()
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


    def mutate_contents(self):
        if not self.children:
            content_mutator = Mutator(self.chunk_content)
            self.chunk_content = content_mutator.mutate_n_times(self.chunk_content, 10)

        else:
            for chunk in self.children.values():
                chunk.mutate_contents()
    
    def add_chunk(self, output):
        if (len(output) == 0):
            return output
        
        new_chunk = random.choice(output)
        if (new_chunk[1].modifiable):
            position = random.randrange(0, len(self.children))
            output.insert(position, new_chunk)

        return output
    
    def remove_chunk(self, output):
        if (len(output) == 0):
            return output
        
        chosen_chunk = random.choice(output)
        if (chosen_chunk[1].modifiable):
            output.remove(chosen_chunk)

        return output
    
    def get_content(self):
        match self.chunk_type:
            case ChunkType.OBJECT:
                return self.get_children()

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

            # Default to string handling
            case _:
                # Return concatenation of children content
                res = ""
                if len(self.children) == 0:
                    return self.chunk_content
                
                for child in self.children.values():
                    # self.logger.log(child)
                    # self.logger.log(child.get_content())
                    res += str(child.get_content())

                return res
            
            
                
    
    def __str__(self):
        return f"SChunk name={self.chunk_name},content={self.chunk_content},num_children={len(self.children)},chunk_mutation_weights={self.chunk_mutation_weights}"
    
    def __repr__(self):
        return f"<SChunk Object name={self.chunk_name},content={self.chunk_content},num_children={len(self.children)},modifiable={self.modifiable},chunk_mutation_weights={self.chunk_mutation_weights}>"
