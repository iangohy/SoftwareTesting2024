class Chunk:
    def __init__(self, chunk_type, start_index, end_index, modifiable, next, children):
        self.chunk_type = chunk_type
        self.start_index = start_index
        self.end_index = end_index
        self.modifiable = modifiable
        self.next = next
        self.children = children

    def add_child(self, child_chunk):
        self.children.append(child_chunk)

    def remove_child(self, child_chunk):
        if child_chunk in self.children:
            self.children.remove(child_chunk)

    def get_chunks(self, file):
        if (open(file, "r") == None):
            return
        
        chunk_file = open(file, "r")
        chunk_lines = chunk_file.readlines()

        for line in chunk_lines:
            # parse
            break

        chunk_file.close()

        return