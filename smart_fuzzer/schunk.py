import random
import configparser
from enum import Enum
from smart_fuzzer.chunk_logger import Logger
from smart_fuzzer.input_models.djangoDict import DjangoDict

class SChunk:
    def __init__(self, chunk_content=None, modifiable=False, next=None, children=[]):
        self.chunk_content = chunk_content  # Content in the chunk
        self.modifiable = modifiable        # modifiable flag
        self.next = next                    # The next chunk
        self.children = children            # List of children chunks
        self.config = configparser.ConfigParser()
        self.logger = Logger("SmartChunk")

    def generate_chunk_tree(self, input_config_seed):
        pass

    def add_next(self, next_chunk):
        pass

    def get_next(self):
        pass

    def add_child(self, child_chunk):
        pass
    

    def mutate(self):
        mutation = random.choice(list(Mutate))
        output = self.children.copy()
        match mutation:
            case Mutate.ADD_CHUNK:
                output = self.add_chunk(output)

            case Mutate.REMOVE_CHUNK:
                output = self.remove_chunk(output)

        output_string = ''
        for chunk in output:
            output_string += chunk.chunk_content
        output_chunk = SChunk()

        return output_chunk

    
    def add_chunk(self, output):
        new_chunk = random.choice(self.children)
        if (new_chunk.modifiable):
            position = random.randrange(0, len(self.children))
            output.insert(position, new_chunk)

        return output
    
    def remove_chunk(self, output):
        chosen_chunk = random.choice(self.children)
        if (chosen_chunk.modifiable):
            output.remove(chosen_chunk)

        return output
        
    def write_output(self, file, output_chunk):
        output_string = ''
        for chunk in output_chunk.children:
            output_string += chunk.chunk_content
        output_string += '\n'

        if (isinstance(self.chunk_type, DjangoDict)):
            output_file = open(file, "a")
            output_file.write(output_string)
            output_file.close()

class Mutate(Enum):
    ADD_CHUNK = 1
    REMOVE_CHUNK = 2