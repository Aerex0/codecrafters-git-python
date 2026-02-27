import sys
import os
import zlib
import hashlib
from pathlib import Path

"""
Permission and type values in the mode field inside a tree object
100644 - Regular file
100755 - Executable file
40000 - Directory (Tree object)

Note that directory mode is 40000, not 040000. Although Git commands like git ls-tree show directory modes as 040000 for readability, the actual mode stored in the tree object is 40000
"""

def get_fileandfolder(SHA: str):
    folderSHA = SHA[:2]
    fileSHA = SHA[2:]
    return folderSHA, fileSHA

def init():
    os.mkdir(".git")
    os.mkdir(".git/objects")
    os.mkdir(".git/refs")
    with open(".git/HEAD", "w") as f:
        f.write("ref: refs/heads/main\n")
    print("Initialized git directory")

def get_tree_contents(tree_bytes):
    i = 0
    modes, names, SHAs = [], [], []

    header_end = tree_bytes.index(b'\0')
    i = header_end +1

    while(i < len(tree_bytes)):
        # mode
        space = tree_bytes.index(b' ', i)
        mode = tree_bytes[i:space].decode()
        modes.append(mode)

        # name
        null_byte = tree_bytes.index(b'\0', space)
        name = tree_bytes[space+1:null_byte].decode()
        names.append(name)

        # SHA (20 raw bytes → convert to hex)
        SHA = tree_bytes[null_byte+1:null_byte+21].hex()
        SHAs.append(SHA)

        # move to next entry
        i = null_byte + 21

    return  modes, names, SHAs

def Blob_content(options, SHA):
    SHA_FOLDER, SHA_FILE = get_fileandfolder(SHA)
    if options == "-p":
        with open(f".git/objects/{SHA_FOLDER}/{SHA_FILE}", "rb") as f:
            compressed_text = f.read()
            text = zlib.decompress(compressed_text)
            text = text.decode("utf-8")
            size = text.split(' ')[1].split('\0')[0]
            content = text.split('\0')[1]
            # print(content) Change this to print(content, end='') to remove the new line
            sys.stdout.write(content)

def create_Blob(options,file):
    if options == "-w":
        with open(file, "r") as f:
            content = f.read()
            header_content = f"blob {len(content)}\0{content}"
            file_hash = hashlib.sha1(header_content.encode()).hexdigest()
            file_folder, file_name = get_fileandfolder(file_hash)
            os.makedirs(f".git/objects/{file_folder}", exist_ok=True)
            with open(f".git/objects/{file_folder}/{file_name}", "wb") as f:
                f.write(zlib.compress(header_content.encode("utf-8")))
            # sys.stdout.write(file_hash)
            return file_hash

def tree():
    if(len(sys.argv) == 3):
        SHA = sys.argv[2]
        SHA_FOLDER, SHA_FILE = get_fileandfolder(SHA)
        with open(f".git/objects/{SHA_FOLDER}/{SHA_FILE}", "rb") as f:
            compressed_text = f.read()
            text = zlib.decompress(compressed_text)
            text = text.decode("utf-8")
            sys.stdout.write(text)

    elif(len(sys.argv) == 4):
        flag = sys.argv[2]
        SHA = sys.argv[3]
        SHA_FOLDER, SHA_FILE = get_fileandfolder(SHA)
        if flag == "--name-only":
            with open(f".git/objects/{SHA_FOLDER}/{SHA_FILE}", "rb") as f:
                compressed_text = f.read()
                text = zlib.decompress(compressed_text) # No need to decode from bytes
                modes, names, SHAs = get_tree_contents(text)
                for name in names:
                    sys.stdout.write(name + "\n")



def write_tree(directory_path="."):
    # Convert string path to a Path object
    path = Path(directory_path)
    
    # Git requires tree content to be sorted by name
    # We use .iterdir() to get all files/folders
    items = sorted(path.iterdir(), key=lambda x: x.name)
    
    content = b"" # Git expects the content to be bytes not hex strings
    
    for item in items:
        # CRITICAL: Always skip the .git directory
        if item.name == ".git":
            continue
            
        if item.is_file():
            file_hash = create_Blob("-w", item)
            content += f"100644 {item.name}\0".encode()+bytes.fromhex(file_hash)
        elif item.is_dir():
            dir_hash = write_tree(item)
            content += f"40000 {item.name}\0".encode()+bytes.fromhex(dir_hash)

    # Create the tree object
    size = len(content)
    tree_content = f"tree {size}\0".encode() + content
    tree_hash = hashlib.sha1(tree_content).hexdigest()
    tree_folder, tree_name = get_fileandfolder(tree_hash)
    os.makedirs(f".git/objects/{tree_folder}", exist_ok=True) # DOES NOT raise an error in case the object folder already exists
    with open(f".git/objects/{tree_folder}/{tree_name}", "wb") as f:
        f.write(zlib.compress(tree_content))
    return tree_hash

def main():
    print("Logs from your program will appear here!", file=sys.stderr)
    
    command = sys.argv[1]
    if command == "init":
        init()
    elif command == "cat-file":
        options = sys.argv[2]
        SHA = sys.argv[3]
        Blob_content(options, SHA)
    elif command == "hash-object":
        options = sys.argv[2]
        file = sys.argv[3]
        SHA_filehash = create_Blob(options, file)
        sys.stdout.write(SHA_filehash)
    elif command == "ls-tree":
        tree()
    elif command == "write-tree":
        SHA_treehash = write_tree()
        sys.stdout.write(SHA_treehash)
    else:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()
