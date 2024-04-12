import configparser
from schunk import SChunk, ChunkType
import logging

logger = logging.getLogger(__name__)

# Chunk Generator that takes in a target config input seed and returns a SChunk Tree
class ChunkTreeGenerator:
    def __init__(self, input_config_seed):
        self.input_config_seed = input_config_seed
        self.config = configparser.ConfigParser()


    def generate_chunk_tree(self):
        self.config.read(self.input_config_seed)
        root = SChunk('root', None, False, {}, {}, ChunkType.OBJECT)
        self.create_child_chunk(root, 'root', None, self.config['root']['children'])

        return root

    def create_child_chunk(self, current_chunk, section_name, chunk_content, chunk_children):
        if chunk_children == 'None':
            if (self.config.has_option(section_name, 'chunkMutationWeights')):
                chunk_mutation_weights = list(map(float, self.config.get(section_name, 'chunkMutationWeights').split()))
                return SChunk(section_name, chunk_content, True, {}, {}, chunk_mutation_weights, ChunkType.STRING)
            return SChunk(section_name, chunk_content, True, {}, {}, chunk_type=ChunkType.STRING)
        else:
            children_sections = self.config.get(section_name, 'children').split()
            for child_section in children_sections:
                # Create intermidiate chunk here
                section_chunk = SChunk(child_section, 
                                       self.config[child_section]['content'], 
                                       self.config[child_section].getboolean("modifiable", True), 
                                       {}, 
                                       {}, 
                                       chunk_type=ChunkType.OBJECT)
                if (self.config.has_option(child_section, 'chunkMutationWeights')):
                    section_chunk.chunk_mutation_weights = list(map(float, self.config.get(child_section, 'chunkMutationWeights').split()))

                child_chunk = self.create_child_chunk(section_chunk,
                                                      child_section, 
                                                      self.config[child_section]['content'], 
                                                      self.config[child_section]['children'])
                if (child_chunk != None):
                    section_chunk.add_child(child_chunk)
                # Append intermidate chunk into current chunk
                current_chunk.add_child(section_chunk)


    # Concatenate entire tree to return a complete input for target application,
    # consider chunks with children of differing chunk types (string and int etc)
    def get_content(self, root):
        pass


