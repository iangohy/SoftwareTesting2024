import configparser
from smart_fuzzer.schunk import SChunk, ChunkType
import logging

logger = logging.getLogger(__name__)

# Chunk Generator that takes in a target config input seed and returns a SChunk Tree
class ChunkTreeGenerator:
    def __init__(self, input_config_seed):
        self.input_config_seed = input_config_seed
        self.config = configparser.ConfigParser()


    def generate_chunk_tree(self):
        self.config.read(self.input_config_seed)
        mutation_weights = [float(i) for i in self.config["root"].get('chunkMutationWeights', "0.33 0.33 0.34").split(" ")]
        content_mutation_probability = float(self.config["root"].get('contentMutationProbability', 0.2))
        root = SChunk('root', chunk_content=None, removable=False, chunk_mutation_weights=mutation_weights, chunk_type=ChunkType.OBJECT, content_mutation_probability=content_mutation_probability)
        self.create_child_chunk(root, 'root', None, self.config.get('root', 'children'))

        return root

    def create_child_chunk(self, current_chunk, section_name, chunk_content, chunk_children):
        if chunk_children == 'None':
            if (self.config.has_option(section_name, 'chunkMutationWeights')):
                chunk_mutation_weights = list(map(float, self.config.get(section_name, 'chunkMutationWeights').split()))
                return current_chunk.set_mutation_weights(chunk_mutation_weights)
            return
        else:
            children_sections = self.config[section_name].get('children', 'None').split()
            for child_section in children_sections:
                # Create intermediate chunk here
                section_chunk_type_config = self.config[child_section].get("type", "object")
                section_chunk_type = ChunkType[section_chunk_type_config.upper()]
                mutation_weights = [float(i) for i in self.config[child_section].get('chunkMutationWeights', "0.33 0.33 0.34").split(" ")]
                content_mutation_probability = float(self.config[child_section].get('contentMutationProbability', 0.2))
                section_chunk = SChunk(child_section, 
                                       self.config[child_section].get('content', 'None'), 
                                       self.config[child_section].getboolean("removable", True), 
                                       {}, 
                                       {},
                                       chunk_mutation_weights=mutation_weights,
                                       chunk_type=section_chunk_type,
                                       content_mutation_probability=content_mutation_probability)
                if (self.config.has_option(child_section, 'chunkMutationWeights')):
                    section_chunk.chunk_mutation_weights = list(map(float, self.config.get(child_section, 'chunkMutationWeights').split()))

                child_chunk = self.create_child_chunk(section_chunk,
                                                      child_section, 
                                                      self.config[child_section].get('content', 'None'), 
                                                      self.config[child_section].get('children', 'None'))
                if (child_chunk != None):
                    section_chunk.add_child(child_chunk)
                # Append intermidate chunk into current chunk
                current_chunk.add_child(section_chunk)


