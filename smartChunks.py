from enum import Enum

class Chunk:
    def __init__(self, id, 
                 type, 
                 start_byte, 
                 end_byte, 
                 modifiable, 
                 next, 
                 children):
        self.id = id                    # id of the chunk, when loaded from chunks file, equals to the hashcode of its chunk identifier string casted to unsigned long
        self.type = type                # hashcode of the chunk type
        self.start_byte = start_byte    # start byte, negative if unknown
        self.end_byte = end_byte        # last byte, negative if unknown
        self.modifiable = modifiable    # modifiable flag
        self.next = next                # next sibling child
        self.children = children        # children chunks

    def get_chunks(self, filespec, data_chunks):
        
        if (open(filespec, "r") == None):
            return
        
        chunk_file = open(filespec, "r")
        chunk_lines = chunk_file.readlines()

        for line in chunk_lines:
            self.add_path(data_chunks, line)

        chunk_file.close()

        return

    def print_tree(self, root):
        return
    
    def print_tree_with_data(self, root, data):
        return
    
    def smart_log_tree(self, root):
        return
    
    def smart_log_tree_with_data(self, root, data):
        return
    
    def delete_chunks(self, node):
        sibling = node

        while (sibling != None):
            tmp = sibling.next

        self.delete_chunks(sibling.children)

        sibling = tmp

        return
    
    def copy_chunks(self, node):
        if (node == None):
            return None
        
        new_node = node
        new_node.next = self.copy_chunks(node.next)
        new_node.children = self.copy_chunks(node.children)

        return
    
    def increase_byte_positions_except_target_children(self, c, target, start_byte, size):
        sibling = c

        while (sibling != None):
            if (sibling.startbyte >= 0 and sibling.start_byte > start_byte):
                sibling.start_byte += size

            if (sibling.end_byte >= 0 and sibling.end_byte > start_byte):
                sibling.end_byte += size
        
        if (sibling != target):
            self.increase_byte_positions_except_target_children(sibling.children, target, start_byte, size)
        
        return
    
    def reduce_byte_position(self, c, start_byte, size):
        sibling = c

        while (sibling != None):
            if (sibling.startbyte >= 0 and sibling.start_byte > start_byte):
                sibling.start_byte -= size

            if (sibling.end_byte >= 0 and sibling.end_byte > start_byte):
                sibling.end_byte -= size
        
        self.reduce_byte_position(sibling.children, start_byte, size)

        return

    def search_and_destroy_chunk(self, c, target_chunk, start_byte, size):
        sibling = c
        ret = c
        prev = None

        while (sibling != None):
            if (sibling == target_chunk):
                tmp = sibling.next

                if (ret == sibling):
                    ret = tmp
                else:
                    prev.next = tmp
                
                self.delete_chunks(sibling.children)
                
                self.reduce_byte_position(tmp, start_byte, size)
                sibling = tmp
                continue

            if (sibling.startbyte >= 0 and sibling.start_byte > start_byte):
                sibling.start_byte -= size

            if (sibling.end_byte >= 0 and sibling.end_byte > start_byte):
                sibling.end_byte -= size

            sibling.children = self.search_and_destroy_chunk(sibling.children, target_chunk, start_byte, size)

            prev = sibling
            sibling = sibling.next

        return ret
    
    def smart_log_tree_hex(self, root):
        return
    
    def smart_log_tree_with_data_hex(self, root, data):
        return
    
    def smart_log_tree_with_data_hex(self, root, data):
        return
    
    def add_path(self, tree, line):
        return

class ReadLineStatus(Enum):
    READ_LINE_OK = 0
    READ_LINE_FILE_ERROR = 1
    READ_LINE_TOO_LONG = 2