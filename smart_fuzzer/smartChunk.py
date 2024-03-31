import random
from enum import Enum
from chunk_logger import Logger
from input_models.djangoDict import DjangoDict

class SmartChunk:
    def __init__(self, chunk_type, chunk_content=None, start_index=0, end_index=0, modifiable=False, next=None, children=[]):
        self.chunk_type = chunk_type        # Sets the dictionary to be used
        self.chunk_content = chunk_content  # Content in the chunk
        self.start_index = start_index      # Start Index of a chunk relative to the full seed input
        self.end_index = end_index          # End Index of a chunk relative to the full seed input
        self.modifiable = modifiable        # modifiable flag
        self.next = next                    # The next chunk
        self.children = children            # List of children chunks
        self.logger = Logger("SmartChunk")

    def add_child(self, child_chunk):
        self.children.append(child_chunk)
    
    def get_chunks(self, seed_string):
        if (isinstance(self.chunk_type, DjangoDict)):
            self.chunk_content = seed_string
            self.start_index = 0
            self.end_index = len(seed_string) - 1

            current_index = 0
            while (seed_string != ''):
                if (self.chunk_type.base_url_dict[0] in seed_string):
                    child_chunk = SmartChunk(DjangoDict(), 
                                        self.chunk_type.base_url_dict[0], 
                                        seed_string.find(self.chunk_type.base_url_dict[0]),
                                        seed_string.find(self.chunk_type.base_url_dict[0]) + len(self.chunk_type.base_url_dict[0]) - 1,
                                        False)
                    self.add_child(child_chunk)
                    seed_string = seed_string.replace(self.chunk_type.base_url_dict[0], '')
                    current_index += len(self.chunk_type.base_url_dict[0])
                
                for endpoint in self.chunk_type.endpoint_dict:
                    if (seed_string.find(endpoint) == 0):
                        child_chunk = SmartChunk(DjangoDict(),
                                            endpoint, 
                                            current_index, 
                                            current_index + len(endpoint) - 1,
                                            True)
                        self.add_child(child_chunk)
                        seed_string = seed_string.replace(endpoint, '')
                        current_index += len(endpoint)

        for child in self.children:
            self.logger.log(child.chunk_content)
        self.logger.log("Chunks created")

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
        output_chunk = SmartChunk(self.chunk_type,
                                  output_string,
                                  0,
                                  len(output_string),
                                  False,
                                  None,
                                  output)

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