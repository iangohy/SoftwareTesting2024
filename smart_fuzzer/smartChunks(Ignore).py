from enum import Enum

class Chunks:
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

    def hash_code(str):
        h = 0
        for c in str:
            if c == '\0':
                break
            h = 31 * h + ord(c)
        
        return h

    def next_lower_chunk(self, path, length, hash, type_hash):
        c = ''
        s = path
        tmp = ''
        last_underscore = ''

        if (path is None):
            length = 0
            return 0
        
        for elem in s:
            c = elem
            if (c != '~' and c != '\n' and c != '\0' and c != ','):
                break

        length = len(s) - len(path)

        if tmp is None:
            tmp = path[:length]
            tmp += '\0'

        hash = self.hash_code(tmp)

        last_underscore = tmp + length - 1
        while last_underscore >= tmp:
            if last_underscore[0] == '_':
                last_underscore[0]  = '\0'
                break
            elif not last_underscore[0].isdigit():
                break
            last_underscore -= 1

        type_hash[0] = self.hash_code(tmp)

        if c == '~':
            return -1
        
        return 0
            
    def split_line_on_comma(self, line, start_byte, end_byte, path, modifiable):
        start = end = line
        str = ''
        READ_LINE_BUFFER_SIZE = 1024

        str = line[:READ_LINE_BUFFER_SIZE]
        if str is None:
            return -1
    
        start = end
        while end.isdigit():
            end += 1
        start_byte[0] = self.atoi(str[start:end])

        start = end
        while end.isdigit():
            end += 1
        end_byte[0] = self.atoi(str[start:end])

        start = end
        c = line[end]
        while c != '\n' and c != '\0' and c != ',':
            c = line[end]
            end += 1
        path[0] = line[start:end - 1]

        modifiable[0] = 0
        if c == ',':
            start = end
            if self.strncmp(line[start:start + 7], "Enabled", 7):
                modifiable[0] = 1

        return 0

    def add_path(self, tree, line):
        next = None
        current_chunk = tree
        non_last = -1

        start_byte, end_byte = 0, 0
        modifiable = ''

        if self.split_line_on_comma(line, start_byte, end_byte, next, modifiable):
            return

        if tree is None:
            length = 0
            h, t = 0, 0

            non_last = self.next_lower_chunk(next, length, h, t)

            if length == 0:
                return

            next = next + length + 1

            current_chunk = Chunk(h, t, -1, -1, modifiable)
            tree = current_chunk
        else:
            length = 0
            h, t = 0, 0

            non_last = self.next_lower_chunk(next, length, h, t)

            if length == 0:
                return

            next = next + length + 1

            if current_chunk.id != h:
                new_chunk = Chunk(h, t, -1, -1, modifiable)
                new_chunk.next = current_chunk.next
                current_chunk.next = new_chunk
                current_chunk = new_chunk

            if not current_chunk.modifiable:
                current_chunk.modifiable = modifiable

        while non_last:
            length = 0
            h, t = 0, 0

            non_last = self.next_lower_chunk(next, length, h, t)

            if length == 0:
                return

            next = next + length + 1

            c = current_chunk.children

            if c is None:
                c = Chunk(h, t, -1, -1, modifiable)
                current_chunk.children = c
                current_chunk = c
            else:
                chunk_found = False
                while c:
                    if c.id == h:
                        current_chunk = c
                        chunk_found = True
                        break
                    c = c.next

                if not chunk_found:
                    c = Chunk(h, t, -1, -1, modifiable)
                    c.next = current_chunk.children
                    current_chunk.children = c
                    current_chunk = c

            if not current_chunk.modifiable:
                current_chunk.modifiable = modifiable

        current_chunk.start_byte = start_byte
        current_chunk.end_byte = end_byte

    def get_chunks(self, filespec, data_chunks):
        
        if (open(filespec, "r") == None):
            return
        
        chunk_file = open(filespec, "r")
        chunk_lines = chunk_file.readlines()

        for line in chunk_lines:
            self.add_path(data_chunks, line)

        chunk_file.close()

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

    def print_whitespace(self, smart_log_mode, amount):
        return
    
    def print_node(self):
        return

    def print_tree(self, root):
        return
    
    def print_tree_with_data(self, root, data):
        return
    
    def smart_log_tree(self, root):
        return
    
    def smart_log_tree_with_data(self, root, data):
        return
    
    def smart_log_tree_hex(self, root):
        return
    
    def smart_log_tree_with_data_hex(self, root, data):
        return
    
    def smart_log_tree_with_data_hex(self, root, data):
        return

    def atoi(self, string):
        return int(string)

    def strncmp(self, s1, s2, n):
        return s1[:n] == s2[:n]

class ReadLineStatus(Enum):
    READ_LINE_OK = 0
    READ_LINE_FILE_ERROR = 1
    READ_LINE_TOO_LONG = 2