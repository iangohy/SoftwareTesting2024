import random
import configparser
from enum import Enum
from smart_fuzzer.chunk_logger import Logger
from smart_fuzzer.mutator import Mutator

class ChunkType(Enum):
    STRING = 1

class ChunkMutate(Enum):
    ADD_CHUNK = 1
    REMOVE_CHUNK = 2
    NO_MUTATION = 3

class SChunk:
    def __init__(self, chunk_id, chunk_name, chunk_content=None, modifiable=False, children={},chunk_type=ChunkType.STRING):
        self.chunk_id = chunk_id            # id of the chunk, starts at 0, id is relative to its position in the children dictionary it is in
        self.chunk_name = chunk_name        # Name of the chunk, corresponds to section name in seed config file
        self.chunk_content = chunk_content  # Content in the chunk
        self.modifiable = modifiable        # modifiable flag
        self.children = children            # List of children chunks
        self.config = configparser.ConfigParser()
        self.logger = Logger("SmartChunk")
        self.type = chunk_type
    
    def get_children(self):
        return self.children
    
    def get_child(self, child_key):
        return self.children[child_key]

    def add_child(self, child_chunk):
        self.children[child_chunk.chunk_id] = child_chunk
    
    # full mutation consists of 2 passes of mutations, 1 pass for chunk mutations, 1 pass for content mutation
    def mutate_chunks(self):
        if not self.children:
            return
        elif not self.modifiable:
            return 
        else:
            mutation = random.choice(list(ChunkMutate))
            output = list(self.children.items())
            match mutation:
                case ChunkMutate.ADD_CHUNK:
                    output = self.add_chunk(output)

                case ChunkMutate.REMOVE_CHUNK:
                    output = self.remove_chunk(output)

                case ChunkMutate.NO_MUTATION:
                    output = output

            self.children = {}
            child_chunk_id = 0
            for tup in output:
                self.children[child_chunk_id] = tup[1]
                child_chunk_id += 1

            for chunk in self.children.values():
                chunk.mutate_chunks()

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
        match self.type:
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
        return f"SChunk id={self.chunk_id},name={self.chunk_name},content={self.chunk_content},num_children={len(self.children)}"
    
    def __repr__(self):
        return f"<SChunk Object id={self.chunk_id},name={self.chunk_name},content={self.chunk_content},num_children={len(self.children)},modifiable={self.modifiable}>"
