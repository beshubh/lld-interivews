# ═══════════════════════════════════════════════════════════════════════════
# REQUIREMENTS
#
# Example (Tic Tac Toe):
#   1. Two players alternate placing X and O on a 3x3 grid.
#   2. A player wins by completing a row, column, or diagonal.
#   Out of Scope: UI, AI opponent, networking
# ═══════════════════════════════════════════════════════════════════════════

# REQUIREMENTS
# - In memory file system allowing users to create directories and files with string content.
# - Supports only absolute unix-style path. '/home/user/file.txt'
# - Supported operations of the file system.
#     - Create a file or dir.
#     - delete a file or dir.
#     - list contents of a dir.
#     - rename directory or file
#     - move a file or dir.
#     - write to a file.
#     - read from a file.
# - There is a single root at `/` and all directories exist somewhere within that hierarchy.
# - Error handling:
#     - creating file in invalid directory should throw errors.
#     - create file/direcotry with the name that already exists should throw error.

# Out of scope: Permissions, UI, Concurrency


# ═══════════════════════════════════════════════════════════════════════════
# ENTITIES & RELATIONSHIPS
#
# Example (Tic Tac Toe):
#   Game, Board, Player
# ═══════════════════════════════════════════════════════════════════════════
- FileSystem, FileSystemEntry, Directory impl FileSystemEntry, File impl FileSystemEntry


# ═══════════════════════════════════════════════════════════════════════════
# CLASS DESIGN
#
# Example (Tic Tac Toe):
#   class Game:
#     - board: Board
#     - currentPlayer: Player
#     + makeMove(row, col) -> bool
# ═══════════════════════════════════════════════════════════════════════════


class FileSystem:

    def __init__(self) -> None:
        self._root = self.create_dir('/')
    
    def create_dir(self, path: str) -> FileSystemEntry:
        pass
    
    def create_file(self, path: str, content: str) -> FileSystemEntry:
        pass
    
    def delete(self, path: str) -> None:
        pass
    
    def list_contents(self, path: str) -> list[FileSystemEntry]:
        # throws if path is a file
        pass
    
    def rename(self, old_path: str, new_name: str) -> None:
        if old_path == '/':
            raise ValueError('Cannot rename root dir')
        fs_entry = self._resolve_path(old_path)
        # remove from parent 
        parent = fs_entry.parent
        if parent.get_child(new_name):
            raise ValueError(f'File with name: {new_name} already exists')
        parent.remove_child(fs_entry)
        # rename, and add to the parent
        fs_entry.name = new_name
        parent.add_child(fs_entry)


    
    def read_file(self, path: str) -> str:
        pass
    
    def write_content(self, path: str, content: str) -> None:
        pass
    
    def move(self, old_path: str, new_path: str) -> None:
        # validate old_path and new_path
        # new_path should be a directory and obviously should exist
        # if the new path parent already has the child with the same name raise the error

        old_fs_entry = self._resolve_path(old_path)
        new_path_dir = self._resolve_path(new_path)
        # cycle detection
        p = new_path_dir
        if old_fs_entry is self._root:
            raise ValueError('cannot move a directory into itself')
        while p != self._root:
            if p is old_fs_entry:
                raise ValueError('cannot move a directory into itself')
            p = p.parent

        if not new_path_dir.is_directory():
            raise ValueError(f'Not a directory: {new_path}')
        if new_path_dir.get_child(old_fs_entry.name):
            raise ValueError(f'Entry with name: {old_fs_entry.name} already exists in: {new_path}')
        
        # remove from old parent
        old_parent = old_fs_entry.parent
        old_parent.remove_child(old_fs_entry)

        # add to new parent
        old_fs_entry.parent = new_path_dir
        new_path_dir.add_child(old_fs_entry)
    
    def _resolve_path(self, path: str) -> FileSystemEntry:
        # throws if path is invalid
        if path == '/':
            return self._root
        parts = [p for p in path.split('/') if p]
        parent = self._root
        for part in parts:
            if not parent.is_directory():
                raise ValueError(f'Not a directory: {parent.name}')
            child = parent.get_child(part)
            if not child:
                raise ValueError(f'No such file or directory: {part}')
            parent = child
        return parent  


class FileSystemEntry(ABC):

    def __init__(self, name: str, parent: FileSystemEntry) -> None:
        self._name = name
        self._parent = parent

    @property 
    def name(self):
        return self._name
    
    @property.setter
    def name(self, new_name: str):
        self._name = new_name
    
    def delete(self, path: str):
        pass
    
    @abstractmethod
    def is_directory(self) -> bool:
        raise NotImplmentedError('method not implemented')
    
    @property
    def path(self):
        pass

    @property
    def parent(self):
        return self._parent
    
    @property.setter
    def parent(self, new_parent: FileSystemEntry) -> None:
        self._parent = new_parent



class Directory(FileSystemEntry)

    def __init__(self, name: str, parent: FileSystemEntry) -> None:
        super().__init__(name, parent)
        self._children: dict[str, FileSystemEntry] = {}
    
    def is_directory(self) -> bool:
        return True
    
    def create_dir(self) -> FileSystemEntry:
        pass
    
    def create_file(self) -> FileSystemEntry:
        pass
    
    def list_contents(self) -> list[FileSystemEntry]:
        pass
    
    def get_child(self, name: str) -> FileSystemEntry | None:
        return self._children.get(name)
    
    def add_child(self, f: FileSystemEntry) -> None:
        self._children[f.name] = f
    
    def remove_child(self, f: FileSystemEntry) -> None:
        del self._children[f.name]


class File(FileSystemEntry):
    def __init__(self, name: str, parent: FileSystemEntry, content: str) -> None:
        super().__init__(name, parent)
        self._content = content
    
    def write_content(self, content: str) -> None:
        pass
    
    def read_file(self) -> str:
        pass


# ═══════════════════════════════════════════════════════════════════════════
# IMPLEMENTATION
# ═══════════════════════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════════════════════
# EXTENSIBILITY
# ═══════════════════════════════════════════════════════════════════════════



class FileSystem:

    def __init__(self) -> None:
        self._root = self.create_dir('/')
    
    def create_dir(self, path: str) -> FileSystemEntry:
        pass
    
    def create_file(self, path: str, content: str) -> FileSystemEntry:
        pass
    
    def delete(self, path: str) -> None:
        pass
    
    def list_contents(self, path: str) -> list[FileSystemEntry]:
        # throws if path is a file
        pass
    
    def rename(self, old_path: str, new_name: str) -> None:
        if old_path == '/':
            raise ValueError('Cannot rename root dir')
        fs_entry = self._resolve_path(old_path)
        # remove from parent 
        parent = fs_entry.parent
        if parent.get_child(new_name):
            raise ValueError(f'File with name: {new_name} already exists')
        parent.remove_child(fs_entry)
        # rename, and add to the parent
        fs_entry.name = new_name
        parent.add_child(fs_entry)


    
    def read_file(self, path: str) -> str:
        pass
    
    def write_content(self, path: str, content: str) -> None:
        pass
    
    def move(self, old_path: str, new_path: str) -> None:
        # validate old_path and new_path
        # new_path should be a directory and obviously should exist
        # if the new path parent already has the child with the same name raise the error
        if old_path < new_path:
            lockA = self._locks[old_path]
            lockB = self._locks[new_path]
        else:
            lockA = self._locks[new_path]
            lockB = self._locks[old_path]
        with lockA:
            with lockB:
                old_fs_entry = self._resolve_path(old_path)
                new_path_dir = self._resolve_path(new_path)
                # cycle detection
                p = new_path_dir
                if old_fs_entry is self._root:
                    raise ValueError('cannot move a directory into itself')
                while p != self._root:
                    if p is old_fs_entry:
                        raise ValueError('cannot move a directory into itself')
                    p = p.parent
    
                if not new_path_dir.is_directory():
                    raise ValueError(f'Not a directory: {new_path}')
                if new_path_dir.get_child(old_fs_entry.name):
                    raise ValueError(f'Entry with name: {old_fs_entry.name} already exists in: {new_path}')
                
                # remove from old parent
                old_parent = old_fs_entry.parent
                old_parent.remove_child(old_fs_entry)
    
                # add to new parent
                old_fs_entry.parent = new_path_dir
                new_path_dir.add_child(old_fs_entry)
    
    def _resolve_path(self, path: str) -> FileSystemEntry:
        # throws if path is invalid
        if path == '/':
            return self._root
        parts = [p for p in path.split('/') if p]
        parent = self._root
        for part in parts:
            if not parent.is_directory():
                raise ValueError(f'Not a directory: {parent.name}')
            child = parent.get_child(part)
            if not child:
                raise ValueError(f'No such file or directory: {part}')
            parent = child
        return parent  